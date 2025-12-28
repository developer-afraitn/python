from __future__ import annotations

import requests
from typing import Optional
from datetime import datetime, timedelta

from app.exceptions import AppError
from app.storage.repo.memoryRepo import MemoryRepo
from app.logging_config import get_logger
from app.utils.datetime_helper import to_date, to_iso_date_str, today_date,gregorian_to_jalali
from app.utils.ai_response_message import success_message
from app.services.ai_agent.hotel.hotel_date_extractor import HotelDateExtractor

logger = get_logger("ai-agent")
memory_repo = MemoryRepo()

class HotelFilter:

    def __init__(self):
        self.user_memory_id = None
        self._city_cache = None
        self._city_cache_at = None
        self.date_extractor = HotelDateExtractor()

    def _load_cities(self) -> dict[str, int]:
        # اگر کش معتبره، همونو بده
        if self._city_cache and self._city_cache_at and self._city_cache_at > datetime.now() - timedelta(hours=6):
            return self._city_cache

        r = requests.get("https://tourgardan.com/api/info/city/search", timeout=10)
        r.raise_for_status()
        payload = r.json()

        # payload["data"] = [{"id":..., "text":"...", ...}, ...]
        cities = {item["text"]: item["id"] for item in payload.get("data", []) if item.get("text") and item.get("id")}

        self._city_cache = cities
        self._city_cache_at = datetime.now()
        return cities

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

        information = self.memory(user_id)
        if information is None:
            information = {"city": None, "check_in": None, "check_out": None}


        city_found = self._extract_city(message)

        
        # ✅ استفاده از کلاس جدید
        new_check_in, new_check_out = self.date_extractor.extract(
            message=message,
            prev_check_in=information.get("check_in"),
            prev_check_out=information.get("check_out"),
        )

        if city_found is not None:
            city_name, city_id = city_found
            information["city"] = city_name
            information["city_id"] = city_id
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
        information['limit'] = 3
        information['page'] = 1
        
        information['passengers'] = [{'adult':1,'child':[]}]

        return success_message(
            message=message,
            type='hotel-search',
            result={
                'filters':information
            },
            request=[])

    def _extract_city(self, message: str) -> Optional[tuple[str, int]]:
        cities = self._load_cities()  # {"کیش": 760013, ...}
        for city_name, city_id in cities.items():
            if city_name in message:
                return city_name, city_id
        return None
 
    @staticmethod
    def hotel_filter_summary_text(information: dict) -> str:
        city = information["city"]

        # تاریخ‌های میلادی (ایزو) -> جلالی با فرمت PHP-like که خودت دادی
        check_in_text = gregorian_to_jalali(information["check_in"], "l j F")
        check_out_text = gregorian_to_jalali(information["check_out"], "l j F Y")

        return f"فیلتر برای شهر {city} با تاریخ ورود {check_in_text} و تاریخ خروج {check_out_text}"
