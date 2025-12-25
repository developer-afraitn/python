from sqlalchemy import inspect
from app.core.db import engine

# مدل‌هایی که می‌خوای اگر پاک شدند برگردند
from app.models.messageHistoryModel import MessageHistory
from app.models.memoryModel import Memory

def repair_missing_tables():
    insp = inspect(engine)
    existing = set(insp.get_table_names())
    required_models = [
            MessageHistory,
            Memory,
        ] 

    for model in required_models:
        if model.__table__.name not in existing:
            model.__table__.create(bind=engine, checkfirst=True)
