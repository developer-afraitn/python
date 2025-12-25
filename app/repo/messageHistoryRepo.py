from sqlalchemy import select, desc
from app.core.db import get_session
from app.models.messageHistoryModel import MessageHistory

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
                .order_by(desc(MessageHistory.created_at))
                .limit(limit)
            )
            rows = db.execute(stmt).all()
            return [r[0] for r in reversed(rows)]
