import os, json, re
from typing import Any, Dict, List, Optional

import requests
import chromadb
from google import genai
from google.genai import types


class HotelComparison:
    """
    Gemini + Chroma RAG over Tourgardan review JSON endpoints
    Public API:
      - index_many(hotel_ids)
      - ask(session_id, question, top_k=8)
    """

    def __init__(
        self,
        base_url_template: str = "https://tourgardan.com/hotel/review/{hotel_id}/obj",
        hotels_map: Optional[Dict[str, str]] = None,
        persist_dir: str = "./chroma_hotels",
        collection_name: str = "hotel_kb",
        embed_model: str = "gemini-embedding-001",
        chat_model: str = "gemini-2.5-flash",
        request_timeout: int = 30,
    ):
        self.base_url_template = base_url_template
        self.hotels_map = hotels_map or {
            "اکسلسیور": "1018483",
            "آریا": "1018392",
            "امیرکبیر": "1002353",
            "کوروش": "1001612",
            "میراژ": "1001477",
            "داریوش": "1000336",
            "سان رایز": "1000354",
            "ترنج": "1001104",
        }
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embed_model = embed_model
        self.chat_model = chat_model
        self.request_timeout = request_timeout

        api_key = 'AIzaSyArWDyyLm5sAaQap1Zl3gJ14j-dB5q_aY0'
        self.client = genai.Client(api_key=api_key)

        # Chroma collection
        self._collection = self._get_collection()

        # In-memory session memory (production: replace with Redis)
        # session_id -> {"last_hotels":[...]}
        self._memory: Dict[str, Dict[str, Any]] = {}

    # -------------------------
    # Public methods (ONLY TWO)
    # -------------------------
    def index_many(self, hotel_ids: List[str]) -> Dict[str, Any]:
        """
        Fetches JSON for each hotel ID and indexes into Chroma.
        Returns per-hotel stats.
        """
        results = []
        for hid in hotel_ids:
            url = self.base_url_template.format(hotel_id=hid)
            payload = self._fetch_json(url)
            docs = self._build_docs(payload, source_url=url, hotel_id=hid)
            stats = self._upsert_docs(docs)
            results.append({"hotel_id": hid, "url": url, "stats": stats})
        return {"status": "indexed", "results": results}

    def ask(self, session_id: str, question: str, top_k: int = 8) -> Dict[str, Any]:
        """
        Answers a question. Keeps conversational memory per session_id.
        If hotel names/ids are mentioned, updates memory.
        If not mentioned, uses last_hotels from memory (follow-up questions).
        """
        resolved = self._resolve_hotels(session_id, question)

        # Constrain retrieval to resolved hotels when possible (better for comparisons/followups)
        allowed = resolved if resolved else None
        hits = self._retrieve(question, top_k=top_k, allowed_hotel_ids=allowed)

        answer = self._generate_answer(question, hits, resolved)

        # Slim debug info
        retrieved = [
            {
                "type": h["meta"].get("type"),
                "hotel_id": h["meta"].get("hotel_id"),
                "review_id": h["meta"].get("review_id"),
                "distance": h["distance"],
                "source_url": h["meta"].get("source_url"),
            }
            for h in hits
        ]

        return {
            "answer": answer,
            "resolved_hotel_ids": resolved,
            "retrieved": retrieved,
        }

    # -------------------------
    # Private helpers
    # -------------------------
    def _get_collection(self):
        ch = chromadb.PersistentClient(path=self.persist_dir)
        try:
            return ch.get_collection(self.collection_name)
        except Exception:
            return ch.create_collection(name=self.collection_name)

    @staticmethod
    def _s(x: Any) -> str:
        if x is None:
            return ""
        if isinstance(x, (dict, list)):
            return json.dumps(x, ensure_ascii=False)
        return str(x)

    def _fetch_json(self, url: str) -> Dict[str, Any]:
        r = requests.get(url, timeout=self.request_timeout)
        r.raise_for_status()
        return r.json()

    def _embed(self, text: str) -> List[float]:
        resp = self.client.models.embed_content(model=self.embed_model, contents=text)
        return resp.embeddings[0].values

    def _build_docs(self, payload: Dict[str, Any], source_url: str, hotel_id: str) -> List[Dict[str, Any]]:
        """
        This endpoint is review-heavy. We index:
          1) hotel summary doc
          2) each review comment doc (objects containing "comment")
        """
        docs: List[Dict[str, Any]] = []
        data = payload.get("data", {}) if isinstance(payload, dict) else {}

        name_fa = self._s(data.get("name_fa"))
        name_en = self._s(data.get("name_en"))
        short_desc = self._s(data.get("short_description_fa"))

        hotel_summary = "\n".join([
            f"SourceURL: {source_url}",
            f"HotelID: {hotel_id}",
            f"NameFA: {name_fa}",
            f"NameEN: {name_en}",
            f"ShortDescriptionFA: {short_desc}",
            "RawHotelData: " + self._s(data),
        ])

        docs.append({
            "id": f"hotel::{hotel_id}",
            "text": hotel_summary,
            "meta": {"type": "hotel", "hotel_id": hotel_id, "name_fa": name_fa, "source_url": source_url}
        })

        def walk(obj: Any):
            if isinstance(obj, dict):
                if "comment" in obj and isinstance(obj["comment"], str):
                    rid = self._s(obj.get("id") or f"rand_{abs(hash(obj['comment']))}")
                    review_text = "\n".join([
                        f"SourceURL: {source_url}",
                        f"HotelID: {hotel_id}",
                        f"HotelNameFA: {name_fa}",
                        f"ReviewID: {rid}",
                        f"UserName: {self._s(obj.get('user_name'))}",
                        f"CreatedAt: {self._s(obj.get('created_at'))}",
                        f"Comment: {obj['comment']}",
                    ])
                    docs.append({
                        "id": f"review::{hotel_id}::{rid}",
                        "text": review_text,
                        "meta": {"type": "review", "hotel_id": hotel_id, "review_id": rid, "source_url": source_url}
                    })
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for it in obj:
                    walk(it)

        walk(data)
        return docs

    def _upsert_docs(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        # best-effort existing ids
        try:
            existing = set(self._collection.get(include=[]).get("ids", []))
        except Exception:
            existing = set()

        added = 0
        for d in docs:
            if d["id"] in existing:
                continue
            self._collection.add(
                ids=[d["id"]],
                documents=[d["text"]],
                metadatas=[d["meta"]],
                embeddings=[self._embed(d["text"])],
            )
            added += 1
        return {"added": added, "built": len(docs)}

    def _extract_hotel_ids_from_question(self, question: str) -> List[str]:
        found: List[str] = []

        # Persian names
        for name, hid in self.hotels_map.items():
            if name in question:
                found.append(hid)

        # numeric ids in question
        for m in re.findall(r"\b(10\d{5,6}|100\d{4,6})\b", question):
            if m not in found:
                found.append(m)

        return found

    def _resolve_hotels(self, session_id: str, question: str) -> List[str]:
        mentioned = self._extract_hotel_ids_from_question(question)
        if mentioned:
            self._memory.setdefault(session_id, {})["last_hotels"] = mentioned
            return mentioned

        return self._memory.get(session_id, {}).get("last_hotels", [])

    def _retrieve(self, question: str, top_k: int, allowed_hotel_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
        q_emb = self._embed(question)
        res = self._collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        hits: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            if allowed_hotel_ids and meta.get("hotel_id") not in allowed_hotel_ids:
                continue
            hits.append({"doc": doc, "meta": meta, "distance": dist})

        # If we filtered out everything, fallback to unfiltered results
        if allowed_hotel_ids and not hits:
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
                hits.append({"doc": doc, "meta": meta, "distance": dist})

        return hits

    def _generate_answer(self, question: str, hits: List[Dict[str, Any]], resolved_hotel_ids: List[str]) -> str:
        context = "\n\n---\n\n".join([h["doc"] for h in hits])

        system_instruction = (
            "تو یک دستیار اطلاعات هتل‌ها هستی. "
            "فقط بر اساس CONTEXT پاسخ بده و حدس نزن. "
            "اگر پاسخ در CONTEXT نبود، دقیقاً بگو: «اطلاعات کافی در داده‌های موجود نیست.» "
            "اگر سوال مقایسه‌ای است، مزایا/معایب هر هتل را فقط از روی داده‌ها کنار هم بگذار. "
            "اگر سوال دنباله‌دار است و کاربر نام هتل را نگفته، از resolved_hotel_ids استفاده کن."
        )

        prompt = f"""resolved_hotel_ids: {resolved_hotel_ids}

CONTEXT:
{context}

Question (FA):
{question}
"""

        resp = self.client.models.generate_content(
            model=self.chat_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            ),
        )
        return resp.text or ""
