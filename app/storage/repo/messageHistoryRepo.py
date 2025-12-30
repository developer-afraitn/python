from sqlalchemy import select, desc
from app.storage.db import get_session
from app.storage.models.messageHistoryModel import MessageHistory

class MessageHistoryRepo:
    def create(self, *, user_id: str, content: str) -> MessageHistory:
        user_id = user_id.strip()
        content = content.strip()
        if not user_id or not content:
            raise ValueError("user_id and content are required")

        with get_session() as db:
            row = MessageHistory(user_id=user_id, role="user", content=content)
            db.add(row)
            db.flush()
            db.refresh(row)
            return row

    def get_recent_user_history(self, user_id: str, limit: int = 5) -> list[str]:
        with get_session() as db:
            stmt = (
                select(MessageHistory.content)
                .where(MessageHistory.user_id == user_id)
                .where(MessageHistory.role == "user")
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
