from __future__ import annotations

import re
from datetime import date
from typing import Optional, Tuple


class HotelDateExtractor:
    """
    Inputs:
      - message: متن کاربر
      - prev_check_in: تاریخ ورود قبلی به صورت string 'YYYY-MM-DD' یا None
      - prev_check_out: تاریخ خروج قبلی به صورت string 'YYYY-MM-DD' یا None

    Output:
      - (new_check_in, new_check_out) هرکدام از نوع date یا None
    """

    DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

    def extract(
        self,
        message: str,
        prev_check_in: Optional[str],
        prev_check_out: Optional[str],
    ) -> Tuple[Optional[date], Optional[date]]:
        matches = self.DATE_RE.findall(message or "")
        if not matches:
            return None, None

        ds = [date(int(y), int(m), int(d)) for (y, m, d) in matches[:2]]
        return (ds[0], None) if len(ds) == 1 else (ds[0], ds[1])
