from __future__ import annotations

import re
from datetime import date
from typing import Optional, Tuple

import jdatetime


class HotelDateExtractor:
    """
    استخراج تاریخ‌های شمسی (YYYY/MM/DD) از متن کاربر
    و تبدیل آن‌ها به تاریخ میلادی (datetime.date)
    """

    DATE_RE = re.compile(r"\b(\d{4})/(\d{2})/(\d{2})\b")

    def extract(
        self,
        message: str,
        prev_check_in: Optional[str],
        prev_check_out: Optional[str],
    ) -> Tuple[Optional[date], Optional[date]]:

        matches = self.DATE_RE.findall(message or "")
        if not matches:
            return None, None

        dates = []
        for y, m, d in matches[:2]:
            g = jdatetime.date(int(y), int(m), int(d)).togregorian()
            dates.append(g)

        return (dates[0], None) if len(dates) == 1 else (dates[0], dates[1])
