from sqlalchemy import String, Integer, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.storage.db import Base


class Memory(Base):
    __tablename__ = "memory"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_memory_user_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        String(128), nullable=False
    )

    information: Mapped[dict] = mapped_column(
        JSONB, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
