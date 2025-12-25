from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple

from app.repo.memoryRepo import MemoryRepo
from app.logging_config import get_logger

logger = get_logger("ai-agent")
memory_repo = MemoryRepo()

@dataclass
class HotelFilterState:
    user_id: str
    city: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class SimpleHotelFilterUpdater:

    # --- ساده‌ترین استخراج ---
    CITIES = ("تهران", "مشهد", "شیراز", "اصفهان", "کیش", "تبریز", "رشت", "یزد", "قم", "اهواز")
    DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

    def memory(self, user_id:str):
        memory=memory_repo.find(user_id=user_id)
        if memory is not None:
            self.user_memory_id=memory.id
            return memory.information
        else : 
            return None;

    def __init__(self):
        self.user_memory_id = None

    def handle(self, user_id: str, message: str):
        new_city = self._extract_city(message)
        new_check_in, new_check_out = self._extract_dates(message)

        information = self.memory(user_id)
        if information is None:
            information={
                'city' : None,
                'check_in' : None,
                'check_out' : None,
            }

        if new_city is not None:
            information["city"]= new_city
        if new_check_in is not None:
            information["check_in"] = new_check_in
        if new_check_out is not None:
            information["check_out"] = new_check_out

        if information.get("check_in") is not None:
            information["check_in"] = information["check_in"].isoformat()

        if information.get("check_out") is not None:
            information["check_out"] = information["check_out"].isoformat()


        if self.user_memory_id :
            memory_repo.update(id=self.user_memory_id,information=information)
        else :
            memory_repo.create(user_id=user_id,information=information)

        return information

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
