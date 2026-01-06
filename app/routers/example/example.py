from __future__ import annotations
from fastapi import APIRouter
from app.logging_config import get_logger

from app.services.example.chromadb import ChromaDb
from app.services.example.hazm import Hazm

router = APIRouter()
logger = get_logger("ai-agent")


@router.get("/chromadb/save")
def chromadb():
    chromadb  = ChromaDb()
    return chromadb.save_list([
        {
            'id': 125,
            'document': "Python یک زبان محبوب برای هوش مصنوعی است",
            'metadata': {'type': 'talk', 'feature': 'search'}
        },
        {
            'id': '', 
            'document': "Go برای برنامه‌های سریع بک‌اند مناسب است",
            'metadata': {'type': 'talk', 'feature': 'comparison'}
        },
        {
            'id': None,  
            'document': "Laravel یک فریم‌ورک PHP است",
            'metadata': {'type': 'talk', 'feature': 'greeting'}
        }
    ])

@router.get("/chromadb/show")
def chromadb():
    chromadb  = ChromaDb()
    return chromadb.get_all()

@router.get("/chromadb/ask")
def chromadb():
    chromadb  = ChromaDb()
    return chromadb.ask("بهترین زبان برای بک‌اند سریع چیست؟",n_results=3)


@router.get("/hazm")
def chromadb():
    processor = Hazm()
    text = "علی امروز به تهران رفت. هوا خیلی خوب بود و او خوشحال شد. اما دیروز روز سخت و ناراحتی داشت."
    result = processor.analyze_text(text)
    return result
