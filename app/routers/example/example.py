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
    text = "علی امروز به تهران رفت و کتابی برای مدرسه خرید."

    result = processor.analyze_text(text)

    print("Original Text:", result["original"])
    print("Normalized:", result["normalized"])
    print("Tokens:", result["tokens"])
    print("Tokens without Stopwords:", result["tokens_no_stopwords"])
    print("Stemmed:", result["stemmed"])
    print("Lemmatized:", result["lemmatized"])
    print("Word Count:", result["word_count"])
    print("Character Count:", result["char_count"])
    print("Most Common Tokens:", result["most_common_tokens"])
    print("Entities (simple):", result["entities"])
