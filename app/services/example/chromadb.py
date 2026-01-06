import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
#from sentence_transformers import SentenceTransformer
import uuid


class ChromaDb:
    def __init__(self, path="./chroma_data"):
        """
        path: مسیر ذخیره دیتا
        embedding_type: "default" یا "sentence_transformer"
        model_name: فقط برای sentence_transformer
        """
        self.embedding_type = "default" # sentence_transformer
        self.model_name = "all-MiniLM-L6-v2"

        # انتخاب embedding
        if self.embedding_type == "default":
            
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            self.embedding_function.model_path = os.path.join(os.getcwd(), "libs/all-MiniLM-L6-v2/model.onnx")
            #self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        elif self.embedding_type == "sentence_transformer":
            #self.st_model = SentenceTransformer(self.model_name)
            self.embedding_function = None  # بعداً دستی اضافه می‌کنیم
        else:
            raise ValueError("embedding_type باید 'default' یا 'sentence_transformer' باشد")

        # ساخت کلاینت Chroma
        self.client = chromadb.Client(
            Settings(persist_directory=path)
        )

        # ایجاد یا دریافت collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base5",
            embedding_function=self.embedding_function  # None برای ST
        )

    # 1️⃣ ذخیره لیست
    def save_list(self, items: list):
        ids = []
        documents = []
        metadatas = []

        for i, item in enumerate(items):
            # اگر id داده نشده یا None → یک UUID بساز
            item_id = item.get('id')
            if not item_id:
                item_id = str(uuid.uuid4())
            ids.append(str(item_id))

            documents.append(item['document'])
            metadata = item.get('metadata', {})
            metadata['id'] = item_id  # همیشه id داخل metadata هم بگذار
            metadatas.append(metadata)

        if self.embedding_type == "default":
            # Chroma خودش embedding می‌سازد
            self.collection.upsert(documents=documents, ids=ids,metadatas=metadatas)
        else:
            # خودمان embedding می‌سازیم
            embeddings = self.st_model.encode(documents).tolist()
            self.collection.upsert(documents=documents, embeddings=embeddings, ids=ids,metadatas=metadatas)
        
        return {"status": "ok", "count": len(documents)}

    # 2️⃣ دیدن اطلاعات ذخیره شده
    def get_all(self):
        return self.collection.get()

    # 3️⃣ پرسیدن سؤال
    def ask(self, question: str, n_results=1):
        if self.embedding_type == "default":
            result = self.collection.query(query_texts=[question], n_results=n_results)
        else:
            # embed سؤال با مدل SentenceTransformer
            q_emb = self.st_model.encode([question]).tolist()
            result = self.collection.query(query_embeddings=q_emb, n_results=n_results)

        return result
