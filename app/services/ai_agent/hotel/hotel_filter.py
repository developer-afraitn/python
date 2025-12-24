from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


@dataclass
class HotelFilterState:
    user_id: str
    city: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class SimpleHotelFilterUpdater:
    """
    DB info (hardcoded):
      POSTGRES_DB=appdb
      POSTGRES_USER=appuser
      POSTGRES_PASSWORD=apppass
      host=postgres
      port=5432

    استفاده:
        updater = SimpleHotelFilterUpdater()
        final_filter = updater(user_id="123", message="هتل در مشهد از 2025-12-28 تا 2025-12-30")
    """

    # --- Hardcoded DB URL (طبق اطلاعات شما) ---
    DATABASE_URL = "postgresql+psycopg://appuser:apppass@postgres:5432/appdb"

    # --- ساده‌ترین استخراج ---
    CITIES = ("تهران", "مشهد", "شیراز", "اصفهان", "کیش", "تبریز", "رشت", "یزد", "قم", "اهواز")
    DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

    # --- ORM داخل کلاس ---
    class Base(DeclarativeBase):
        pass

    class UserHotelFilter(Base):
        __tablename__ = "user_hotel_filters"

        user_id: Mapped[str] = mapped_column(primary_key=True)
        city: Mapped[Optional[str]]
        check_in: Mapped[Optional[date]]
        check_out: Mapped[Optional[date]]

    def __init__(self) -> None:
        self.engine = create_engine(self.DATABASE_URL, future=True)
        # اگر جدول را از قبل با migration ساختی، می‌تونی این خط را حذف کنی
        self.Base.metadata.create_all(self.engine)

    def __call__(self, user_id: str, message: str) -> HotelFilterState:
        new_city = self._extract_city(message)
        new_check_in, new_check_out = self._extract_dates(message)

        with Session(self.engine) as db:
            row = db.execute(
                select(self.UserHotelFilter).where(self.UserHotelFilter.user_id == user_id)
            ).scalar_one_or_none()

            if row is None:
                row = self.UserHotelFilter(user_id=user_id, city=None, check_in=None, check_out=None)
                db.add(row)

            if new_city is not None:
                row.city = new_city
            if new_check_in is not None:
                row.check_in = new_check_in
            if new_check_out is not None:
                row.check_out = new_check_out

            db.commit()

            return HotelFilterState(
                user_id=row.user_id,
                city=row.city,
                check_in=row.check_in,
                check_out=row.check_out,
            )

    def _extract_city(self, message: str) -> Optional[str]:
        for c in self.CITIES:
            if c in message:
                return c
        return None

    def _extract_dates(self, message: str) -> Tuple[Optional[date], Optional[date]]:
        matches = self.DATE_RE.findall(message)
        if not matches:
            return None, None
        ds = [date(int(y), int(m), int(d)) for (y, m, d) in matches[:2]]
        return (ds[0], None) if len(ds) == 1 else (ds[0], ds[1])
