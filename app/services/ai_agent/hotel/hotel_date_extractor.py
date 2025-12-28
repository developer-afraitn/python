from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Tuple

import jdatetime


class HotelDateExtractor:
    DATE_RE = re.compile(r"\b(\d{4})/(\d{2})/(\d{2})\b")

    CHECK_IN_HINT = re.compile(r"(ورود|تاریخ ورود)")
    CHECK_OUT_HINT = re.compile(r"(خروج|تاریخ خروج)")
    RANGE_HINT = re.compile(r"(از.*تا)")

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
            for y, m, d in matches
        ]

        # هیچ تاریخی نیست
        if not dates:
            return prev_ci, prev_co

        has_in = bool(self.CHECK_IN_HINT.search(message))
        has_out = bool(self.CHECK_OUT_HINT.search(message))
        has_range = bool(self.RANGE_HINT.search(message))

        # بازه یا هر دو صراحتاً گفته شده
        if has_range or (has_in and has_out):
            if len(dates) >= 2:
                return dates[0], dates[1]

        # فقط ورود
        if has_in and dates:
            new_ci = dates[0]
            if prev_ci and prev_co:
                nights = (prev_co - prev_ci).days
                return new_ci, new_ci + timedelta(days=nights)
            return new_ci, None

        # فقط خروج
        if has_out and dates:
            return prev_ci, dates[-1]

        # fallback: دو تاریخ → هر دو
        if len(dates) >= 2:
            return dates[0], dates[1]

        # fallback: یک تاریخ → ورود
        return dates[0], prev_co
