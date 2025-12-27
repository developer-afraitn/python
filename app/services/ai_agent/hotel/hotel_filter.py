from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple
from datetime import datetime, timedelta

from app.exceptions import AppError
from app.storage.repo.memoryRepo import MemoryRepo
from app.logging_config import get_logger
from app.utils.datetime_helper import to_date, to_iso_date_str, today_date,gregorian_to_jalali

logger = get_logger("ai-agent")
memory_repo = MemoryRepo()

@dataclass
class HotelFilterState:
    user_id: str
    city: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class HotelFilter:

    # --- ساده‌ترین استخراج ---
    CITIES = ("تهران", "مشهد", "شیراز", "اصفهان", "کیش", "تبریز", "رشت", "یزد", "قم", "اهواز")
    DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

    def __init__(self):
        self.user_memory_id = None

    def memory(self, user_id: str):
        memory = memory_repo.find(user_id=user_id)
        if memory is not None:
            self.user_memory_id = memory.id

            # اگر بیشتر از ۱۰ ساعت گذشته، مموری را نادیده بگیر
            if memory.updated_at < datetime.now() - timedelta(hours=10):
                return None

            return memory.information
        return None

    def handle(self, user_id: str, message: str):
        new_city = self._extract_city(message)
        new_check_in, new_check_out = self._extract_dates(message)

        information = self.memory(user_id)
        if information is None:
            information = {"city": None, "check_in": None, "check_out": None}

        if new_city is not None:
            information["city"] = new_city
        if new_check_in is not None:
            information["check_in"] = new_check_in
        if new_check_out is not None:
            information["check_out"] = new_check_out

        # BUGFIX: safe serialize (date -> str), keep str as-is
        information["check_in"] = to_iso_date_str(information.get("check_in")) or information.get("check_in")
        information["check_out"] = to_iso_date_str(information.get("check_out")) or information.get("check_out")

        # persist
        if self.user_memory_id:
            memory_repo.update(id=self.user_memory_id, information=information)
        else:
            memory_repo.create(user_id=user_id, information=information)

        # required fields
        required_fields = ["city", "check_in", "check_out"]
        missing = [f for f in required_fields if not information.get(f)]
        if missing:
            raise AppError(
                status=400,
                message="اطلاعات کافی نیست.",
                data=None,
                detail={"missing_fields": missing},
            )

        # date rules (assume format always valid)
        ci = to_date(information.get("check_in"))
        co = to_date(information.get("check_out"))
        t = today_date()

        if ci < t:
            raise AppError(
                status=400,
                message="تاریخ ورود باید بزرگ‌تر یا مساوی امروز باشد.",
                data=None,
                detail={"check_in": ci.isoformat(), "today": t.isoformat()},
            )

        if co <= ci:
            raise AppError(
                status=400,
                message="تاریخ خروج باید بعد از تاریخ ورود باشد.",
                data=None,
                detail={"check_in": ci.isoformat(), "check_out": co.isoformat()},
            )
        message=self.hotel_filter_summary_text(information)
        return {'message':message,'information':information}

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
    
    @staticmethod
    def hotel_filter_summary_text(information: dict) -> str:
        city = information["city"]

        # تاریخ‌های میلادی (ایزو) -> جلالی با فرمت PHP-like که خودت دادی
        check_in_text = gregorian_to_jalali(information["check_in"], "l j F")
        check_out_text = gregorian_to_jalali(information["check_out"], "l j F Y")

        return f"فیلتر برای شهر {city} با تاریخ ورود {check_in_text} و تاریخ خروج {check_out_text}"
