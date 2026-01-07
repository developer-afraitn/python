from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.storage.db import Base


class ApiLog(Base):
    __tablename__ = "api_log"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    params: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    request_body: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    headers: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    response: Mapped[dict | str | None] = mapped_column(
        JSONB,
        nullable=True
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
