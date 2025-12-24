# repo.py
from __future__ import annotations

from typing import List
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.config.models import ChatMessage


def add_user_message(db: Session, user_id: str, content: str) -> ChatMessage:
    msg = ChatMessage(user_id=user_id, role="user", content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_recent_user_history(db: Session, user_id: str, limit: int = 5) -> List[str]:
    stmt = (
        select(ChatMessage.content)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.role == "user")
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [r[0] for r in reversed(rows)]
