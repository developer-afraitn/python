from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Tuple

import jdatetime


class HotelDateExtractor:
    DATE_RE = re.compile(r"\b(\d{4})/(\d{2})/(\d{2})\b")

    def extract(
        self,
        message: str,
        prev_check_in: Optional[str],
        prev_check_out: Optional[str],
    ) -> Tuple[Optional[date], Optional[date]]:

        prev_ci = date.fromisoformat(prev_check_in) if prev_check_in else None
        prev_co = date.fromisoformat(prev_check_out) if prev_check_out else None

        matches = self.DATE_RE.findall(message or "")
        dates = [
            jdatetime.date(int(y), int(m), int(d)).togregorian()
            for y, m, d in matches[:2]
        ]

        # 1) هیچ تاریخی پیدا نشد
        if not dates:
            return prev_ci, prev_co

        # 2) هر دو تاریخ پیدا شد
        if len(dates) >= 2:
            return dates[0], dates[1]

        found = dates[0]

        # 3) فقط یک تاریخ پیدا شد
        if prev_ci and prev_co:
            nights = (prev_co - prev_ci).days

            # فقط تاریخ خروج عوض شده
            if found == prev_co:
                return prev_ci, found

            # تاریخ ورود عوض شده، خروج = همان تعداد شب قبل
            return found, found + timedelta(days=nights)

        # فقط تاریخ ورود پیدا شده و قبلی نداریم
        return found, None
