from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Tuple
from app.logging_config import get_logger

import jdatetime
logger = get_logger("ai-agent")


class HotelDateExtractor:
    DATE_RE = re.compile(r"\b(\d{4})/(\d{1,2})/(\d{1,2})\b")
    WORD_DATE_RE = re.compile(
        r"\b(?:شنبه|یکشنبه|دوشنبه|سه‌شنبه|سه شنبه|چهارشنبه|پنجشنبه|جمعه)?\s*"
        r"(\d{1,2})\s*(فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s*(\d{4})?\b"
    )
    RELATIVE_RE = re.compile(r"\b(امروز|فردا|پس\s*فردا)\b")
    DURATION_RE = re.compile(r"\bبه\s*مدت\s*(\d+)\s*شب\b")
    MONTH_MAP = {
        "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4, "مرداد": 5, "شهریور": 6,
        "مهر": 7, "آبان": 8, "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12,
    }

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

        msg = message or ""

        matches = self.DATE_RE.findall(msg)
        dates = [
            jdatetime.date(int(y), int(m), int(d)).togregorian()
            for y, m, d in matches
        ]

        # اگر تاریخ عددی نبود، تاریخ متنی مثل "25 دی 1404" یا "25 دی" رو بخون
        if not dates:
            jalali_year_default = jdatetime.date.today().year
            word_matches = self.WORD_DATE_RE.findall(msg)
            dates = [
                jdatetime.date(
                    int(y) if y else jalali_year_default,
                    self.MONTH_MAP[mon],
                    int(day),
                ).togregorian()
                for (day, mon, y) in word_matches
            ]
        logger.info(
            "date_detected",
            dates=dates,
        )
        # اگر تاریخ صریح پیدا نشد، تاریخ نسبی مثل امروز/فردا/پس‌فردا + مدت شب را هندل کن
        if not dates:
            msg = message or ""

            rel = self.RELATIVE_RE.search(msg)
            dur = self.DURATION_RE.search(msg)

            if rel:
                base_j = jdatetime.date.today()
                word = rel.group(1).replace(" ", "")

                offset = 0 if word == "امروز" else (1 if word == "فردا" else 2)
                ci_j = base_j + timedelta(days=offset)
                ci_g = ci_j.togregorian()

                # اگر مدت شب گفته شده بود، خروج را بر اساس آن بساز
                if dur:
                    nights = int(dur.group(1))
                    return ci_g, ci_g + timedelta(days=nights)

                # اگر فقط تاریخ نسبی بود، مثل حالت "فقط ورود" رفتار کن (با حفظ شب‌های قبلی اگر داریم)
                if prev_ci and prev_co:
                    nights = (prev_co - prev_ci).days
                    return ci_g, ci_g + timedelta(days=nights)

                return ci_g, None

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
