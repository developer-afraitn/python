from sqlalchemy import select, desc, func
from app.storage.db import get_session
from app.storage.models.messageHistoryModel import MessageHistory

class MessageHistoryRepo:
    def create(self, *, user_id: str, message: str) -> MessageHistory:
        user_id = user_id.strip()
        message = message.strip()
        if not user_id or not message:
            raise ValueError("user_id and message are required")

        with get_session() as db:
            row = MessageHistory(user_id=user_id, message=message)
            db.add(row)
            db.commit()
            #db.flush()
            db.refresh(row)
            return row

    def get_recent_user_history(self, user_id: str, limit: int = 5) -> list[str]:
        with get_session() as db:
            stmt = (
                select(MessageHistory.message)
                .where(MessageHistory.user_id == user_id)
                #.where(MessageHistory.role == "user")
                .order_by(desc(MessageHistory.id))
                .limit(limit)
            )
            rows = db.execute(stmt).all()
            return [r[0] for r in reversed(rows)]
        
    def list(self , page: int = 1, limit: int = 20) -> list[dict]:
        offset = (page - 1) * limit
        with get_session() as db:
            stmt = (
                select(MessageHistory)
                .order_by(desc(MessageHistory.id))
                .limit(limit)
                .offset(offset)
            )
            objs = db.execute(stmt).scalars().all()
            objs = list(reversed(objs))

            return [
                {col.name: getattr(o, col.name) for col in MessageHistory.__table__.columns}
                for o in objs
            ]


    def update(self, *, id: int, updates: dict) -> MessageHistory | None:
        with get_session() as db:
            row = db.get(MessageHistory, id)
            if row is None:
                return None

            # ویرایش هر ستونی که در updates آمده
            for key, value in updates.items():
                if hasattr(row, key):  # بررسی اینکه ستون وجود دارد
                    setattr(row, key, value)

            row.updated_at = func.now()
            db.add(row)
            db.commit()
            db.refresh(row)
            return row