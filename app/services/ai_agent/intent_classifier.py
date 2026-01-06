from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Deque
from collections import deque
import re
from app.logging_config import get_logger

from app.storage.repo.messageHistoryRepo import MessageHistoryRepo

# --- Optional: Persian normalization (Hazm) ---
from hazm import Normalizer

logger = get_logger("ai-agent")
history_repo = MessageHistoryRepo()


class Intent(str, Enum):
    FILTER = "filter"
    COMPARISON = "comparison"
    GREETING = "greeting"
    OTHER = "other"


@dataclass
class RuleConfig:
    greeting_keywords: Tuple[str, ...] = (
        "سلام", "درود", "وقت بخیر", "صبح بخیر", "عصر بخیر", "شب بخیر",
        "hi", "hello", "hey", "سلام علیکم",
    )

    comparison_keywords: Tuple[str, ...] = (
        "مقایسه", "کدوم بهتره", "کدام بهتره", "بهتره یا", "بهتر است یا",
        "فرقشون", "تفاوت", "بین این", "بین اون", "بین اینا",
        "compare", "vs", "versus",
    )

    filter_keywords: Tuple[str, ...] = (
        "قیمت", "ارزون", "ارزان", "گرون", "گران", "بودجه", "تخفیف",
        "صبحانه", "پارکینگ", "استخر", "سونا", "جکوزی", "wifi", "وای فای",
        "ستاره", "۴ ستاره", "5 ستاره", "لوکس", "نزدیک", "فاصله",
        "ورود", "خروج", "تاریخ", "امشب", "فردا", "پس فردا",
        "اتاق", "نفر", "مسافر", "اقامت",
        # کمک‌کننده برای سناریوی شما:
        "هتل",
    )

    # Regex patterns for numeric signals (price, nights, guests, dates-ish)
    price_pattern: re.Pattern = re.compile(
        r"(\d{1,3}(?:[,\s]\d{3})+|\d+)\s*(تومان|ریال|دلاری?|usd|\$|یورو|eur|€)?",
        re.IGNORECASE,
    )
    date_like_pattern: re.Pattern = re.compile(
        r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})|(\d{1,2}[-/]\d{1,2})",
        re.IGNORECASE,
    )
    nights_pattern: re.Pattern = re.compile(r"(\d+)\s*(شب|روز)", re.IGNORECASE)
    guests_pattern: re.Pattern = re.compile(r"(\d+)\s*(نفر|مسافر)", re.IGNORECASE)


@dataclass
class MLConfig:
    enabled: bool = False  # شما فعلاً ML نمی‌خواید؛ اگر خواستید True کنید
    min_confidence: float = 0.55


class IntentClassifier:
    """
    Fast intent classifier for a hotel-only chat:
    - greeting only from CURRENT message (not full history)
    - comparison/filter can use limited history context
    """

    def __init__(
        self,
        rule_config: Optional[RuleConfig] = None,
        ml_config: Optional[MLConfig] = None,
        model: Optional[object] = None,
        vectorizer: Optional[object] = None,
        history_window: int = 5,
    ):
        self.rules = rule_config or RuleConfig()
        self.ml = ml_config or MLConfig()
        self.model = model
        self.vectorizer = vectorizer
        self.history_window = history_window

        self.normalizer = Normalizer()

    def predict(self, message: str, history: List[str] | Deque[str] | None = None) -> str:
        """
        Returns ONLY one word: filter | comparison | greeting | other
        """
        full_text = self._build_context(message, history)
        full_text_norm = self._normalize(full_text)
        current_norm = self._normalize(message)

        # 1) Rule-based (fast)
        intent = self._predict_by_rules(full_text=full_text_norm, current_message=current_norm)
        if intent is not None:
            return intent.value

        # 2) ML fallback (optional)
        if self.ml.enabled and self.model is not None and self.vectorizer is not None:
            intent_ml, conf = self._predict_by_ml(full_text_norm)
            if intent_ml is not None and conf >= self.ml.min_confidence:
                return intent_ml.value

        return Intent.OTHER.value

    # --------- Context & normalization ---------
    def _build_context(self, message: str, history: List[str] | Deque[str] | None) -> str:
        if not history:
            return message

        if isinstance(history, deque):
            last_msgs = list(history)[-self.history_window :]
        else:
            last_msgs = history[-self.history_window :]

        return " \n ".join(last_msgs + [message])

    def _normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = self.normalizer.normalize(text)
        return text

    # --------- Rule-based engine ---------
    def _predict_by_rules(self, full_text: str, current_message: str) -> Optional[Intent]:
        """
        Key fix:
        - greeting is detected ONLY from current_message
        - comparison/filter can consider full_text (history + message)
        """
        # Greeting only from current message
        if self._contains_any(current_message, self.rules.greeting_keywords):
            # اگر پیام عملاً فقط سلام/احوال‌پرسی بود
            if len(current_message.split()) <= 2:
                return Intent.GREETING
            # اگر همراه با درخواست هتل بود، بریم سراغ filter
            # (پس return نمی‌کنیم)

        # Comparison next (use context)
        if self._contains_any(full_text, self.rules.comparison_keywords):
            return Intent.COMPARISON

        # Filter signals (use context)
        if self._looks_like_filter(full_text):
            return Intent.FILTER

        # اگر پیام فقط سلام نبود و هیچ سیگنالی نبود:
        if self._contains_any(current_message, self.rules.greeting_keywords):
            return Intent.GREETING

        return None

    def _looks_like_filter(self, text: str) -> bool:
        if self._contains_any(text, self.rules.filter_keywords):
            return True
        if self.rules.price_pattern.search(text):
            return True
        if self.rules.date_like_pattern.search(text):
            return True
        if self.rules.nights_pattern.search(text):
            return True
        if self.rules.guests_pattern.search(text):
            return True
        return False

    @staticmethod
    def _contains_any(text: str, keywords: Tuple[str, ...]) -> bool:
        t = text.lower()
        for kw in keywords:
            if kw.lower() in t:
                return True
        return False

    # --------- ML fallback (sklearn-style) ---------
    def _predict_by_ml(self, text: str) -> Tuple[Optional[Intent], float]:
        try:
            X = self.vectorizer.transform([text])

            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X)[0]
                idx = int(proba.argmax())
                conf = float(proba[idx])
                label = self.model.classes_[idx]
                return self._map_label_to_intent(label), conf

            if hasattr(self.model, "decision_function"):
                scores = self.model.decision_function(X)
                if hasattr(scores, "__len__") and len(getattr(scores, "shape", [])) == 2:
                    scores = scores[0]
                else:
                    scores = [float(scores)]  # type: ignore

                scores = [float(s) for s in scores]
                mx = max(scores)
                exps = [pow(2.718281828, s - mx) for s in scores]
                ssum = sum(exps) or 1.0
                probs = [e / ssum for e in exps]
                idx = int(max(range(len(probs)), key=lambda i: probs[i]))
                conf = float(probs[idx])
                label = self.model.classes_[idx]
                return self._map_label_to_intent(label), conf

            label = self.model.predict(X)[0]
            return self._map_label_to_intent(label), 1.0

        except Exception:
            return None, 0.0

    @staticmethod
    def _map_label_to_intent(label: str) -> Optional[Intent]:
        label = str(label).strip().lower()
        if label in ("filter", "f"):
            return Intent.FILTER
        if label in ("comparison", "compare", "c"):
            return Intent.COMPARISON
        if label in ("greeting", "greet", "g"):
            return Intent.GREETING
        if label in ("other", "o"):
            return Intent.OTHER
        return None


class IntentService:
    """
    DB Orchestration layer:
    - fetch history by user_id
    - predict intent
    - store new message
    API layer فقط (user_id, message) پاس می‌دهد.
    """

    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        history_limit: int = 5,
    ):
        self.classifier = classifier or IntentClassifier()
        self.history_limit = history_limit

    def detect_intent(self, user_id: str, message: str) -> str:

        history =history_repo.get_recent_user_history(user_id=user_id, limit=self.history_limit)
        print('history',history)
        intent = self.classifier.predict(message=message, history=history)
        print('intent',intent)
        # logger.info(
        #     "intent_detected",
        #     intent=intent,
        #     user_id=user_id,
        #     message=message,
        #     history=history,
        # )
        history_repo.create(user_id=user_id, content=message)
        return intent
