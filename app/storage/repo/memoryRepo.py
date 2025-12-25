from sqlalchemy import select, func
from app.storage.db import get_session
from app.storage.models.memoryModel import Memory


class MemoryRepo:
    def create(self, *, user_id: str, information: dict) -> Memory:
        with get_session() as db:
            row = Memory(user_id=user_id, information=information)
            db.add(row)
            db.flush()
            db.refresh(row)
            return row

    def update(self, *, id: int, information: dict) -> Memory | None:
        with get_session() as db:
            row = db.get(Memory, id)
            if row is None:
                return None

            row.information = information
            row.updated_at = func.now()
            db.add(row)
            db.flush()
            db.refresh(row)
            return row

    def find(self, *, user_id: str) -> Memory | None:
        with get_session() as db:
            return db.execute(
                select(Memory).where(Memory.user_id == user_id)
            ).scalar_one_or_none()
