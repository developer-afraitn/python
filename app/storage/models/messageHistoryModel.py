from sqlalchemy import String, Integer, DateTime, Index, func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.storage.db import Base

class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    #role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant"
    message: Mapped[str] = mapped_column(String(4000))
    processed_message: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    response: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)

Index("ix_chat_user_time", MessageHistory.user_id, MessageHistory.created_at)
