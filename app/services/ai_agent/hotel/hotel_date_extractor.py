from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional, Tuple, List
from app.logging_config import get_logger

import jdatetime

logger = get_logger("ai-agent")


class HotelDateExtractor:
    # -------------------- Detect Jalali formats in raw text --------------------
    # 1404/10/29
    NUM_JDATE_RE = re.compile(r"\b(\d{4})/(\d{1,2})/(\d{1,2})\b")

    # شنبه 29 دی 1404  |  29 دی  |  4 بهمن
    WORD_JDATE_RE = re.compile(
        r"\b(?:شنبه|یکشنبه|دوشنبه|سه‌شنبه|سه شنبه|چهارشنبه|پنجشنبه|جمعه)?\s*"
        r"(\d{1,2})\s*(فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\s*(\d{4})?\b"
    )

    MONTH_MAP = {
        "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4, "مرداد": 5, "شهریور": 6,
        "مهر": 7, "آبان": 8, "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12,
    }

    # -------------------- Standard bracket formats --------------------
    # [1404-10-29]  (Jalali inside brackets)
    BRACKET_JALALI_RE = re.compile(r"\[(\d{4})-(\d{2})-(\d{2})\]")

    # [2026-01-19]  (Gregorian inside brackets)
    BRACKET_GREG_RE = re.compile(r"\[(\d{4})-(\d{2})-(\d{2})\]")

    # -------------------- Hints/policy --------------------
    CHECK_IN_HINT = re.compile(r"(ورود|تاریخ ورود)")
    CHECK_OUT_HINT = re.compile(r"(خروج|تاریخ خروج)")
    RANGE_HINT = re.compile(r"(از.*تا)")

    # Relative + duration (normalized, no typos assumed)
    RELATIVE_RE = re.compile(r"\b(امروز|فردا|پس\s*فردا)\b")
    DURATION_RE = re.compile(r"\b(\d+)\s*شب\b")

    def extract(
        self,
        message: str,
        prev_check_in: Optional[str]|None,
        prev_check_out: Optional[str]|None,
        prev_nights: Optional[int]|None,
    ) -> Tuple[Optional[date], Optional[date], Optional[int]]:
        """
        ورودی:
          - message: متن کاربر
          - prev_check_in: 'YYYY-MM-DD' یا None (میلادی)
          - prev_check_out: 'YYYY-MM-DD' یا None (میلادی)
          - prev_nights: تعداد شب قبلی یا None

        خروجی:
          - new_check_in: datetime.date یا None (میلادی)
          - new_check_out: datetime.date یا None (میلادی)
          - new_nights: int یا None
          - msg_jalali: متن با تاریخ‌های شمسی داخل براکت [YYYY-MM-DD] (شمسی)
          - msg_greg: متن با تاریخ‌های میلادی داخل براکت [YYYY-MM-DD] (میلادی)
          - extracted_dates: تاریخ‌های میلادی استخراج‌شده از msg_greg (به ترتیب وقوع)
        """

        prev_ci = date.fromisoformat(prev_check_in) if prev_check_in else None
        prev_co = date.fromisoformat(prev_check_out) if prev_check_out else None

        raw_msg = message or ""

        msg_jalali = self._rewrite_to_jalali_brackets(raw_msg, prev_ci, prev_co)
        logger.info("msg_jalali", msg=msg_jalali)

        msg_greg = self._rewrite_jalali_brackets_to_gregorian(msg_jalali)
        logger.info("msg_greg", msg=msg_greg)

        extracted_dates = self._extract_gregorian_bracket_dates(msg_greg)
        logger.info("dates_extracted", dates=[d.isoformat() for d in extracted_dates])

        duration = self._extract_duration_nights(raw_msg)
        logger.info("duration_detected", nights=duration)

        new_ci, new_co = self._apply_policy(
            message=raw_msg,
            dates=extracted_dates,
            duration_nights=duration,
            prev_ci=prev_ci,
            prev_co=prev_co,
            prev_nights=prev_nights,
        )

        new_nights = self._compute_nights(new_ci, new_co, prev_nights)

        return new_ci, new_co, new_nights

    def _default_jalali_year(self, prev_ci: Optional[date], prev_co: Optional[date]) -> int:
        if prev_ci:
            return jdatetime.date.fromgregorian(date=prev_ci).year
        if prev_co:
            return jdatetime.date.fromgregorian(date=prev_co).year
        return jdatetime.date.today().year

    def _rewrite_to_jalali_brackets(self, msg: str, prev_ci: Optional[date], prev_co: Optional[date]) -> str:
        jy_default = self._default_jalali_year(prev_ci, prev_co)
        replacements = []

        # 1) 1404/10/29 -> [1404-10-29]
        for m in self.NUM_JDATE_RE.finditer(msg):
            y, mo, d = m.groups()
            y_i = int(y)
            mo_i = int(mo)
            d_i = int(d)
            repl = f"[{y_i:04d}-{mo_i:02d}-{d_i:02d}]"
            replacements.append((m.start(), m.end(), repl))

        # 2) 29 دی 1404 / 29 دی / شنبه 29 دی -> [1404-10-29]
        for m in self.WORD_JDATE_RE.finditer(msg):
            day_s, mon_name, y_s = m.groups()
            y_i = int(y_s) if y_s else jy_default
            mo_i = self.MONTH_MAP[mon_name]
            d_i = int(day_s)
            repl = f"[{y_i:04d}-{mo_i:02d}-{d_i:02d}]"
            replacements.append((m.start(), m.end(), repl))

        # 3) نسبی (امروز/فردا/پس فردا) -> [YYYY-MM-DD] (شمسی داخل براکت)
        # NOTE: اینجا شمسیِ امروز را درون براکت می‌نویسیم تا مرحله بعد به میلادی تبدیل کند
        rel = self.RELATIVE_RE.search(msg)
        if rel:
            base_j = jdatetime.date.today()
            word = rel.group(1).replace(" ", "")
            offset = 0 if word == "امروز" else (1 if word == "فردا" else 2)
            ci_j = base_j + timedelta(days=offset)
            repl = f"[{ci_j.year:04d}-{ci_j.month:02d}-{ci_j.day:02d}]"
            replacements.append((rel.start(), rel.end(), repl))

        if not replacements:
            return msg

        replacements.sort(key=lambda x: x[0], reverse=True)
        out = msg
        for start, end, repl in replacements:
            out = out[:start] + repl + out[end:]
        return out

    def _rewrite_jalali_brackets_to_gregorian(self, msg_jalali: str) -> str:
        replacements = []
        for m in self.BRACKET_JALALI_RE.finditer(msg_jalali):
            y, mo, d = m.groups()
            j = jdatetime.date(int(y), int(mo), int(d))
            g = j.togregorian()
            repl = f"[{g.isoformat()}]"
            replacements.append((m.start(), m.end(), repl))

        if not replacements:
            return msg_jalali

        replacements.sort(key=lambda x: x[0], reverse=True)
        out = msg_jalali
        for start, end, repl in replacements:
            out = out[:start] + repl + out[end:]
        return out

    def _extract_gregorian_bracket_dates(self, msg_greg: str) -> List[date]:
        out: List[date] = []
        for m in self.BRACKET_GREG_RE.finditer(msg_greg):
            y, mo, d = m.groups()
            try:
                out.append(date(int(y), int(mo), int(d)))
            except ValueError:
                continue
        return out

    def _extract_duration_nights(self, msg: str) -> Optional[int]:
        m = self.DURATION_RE.search(msg or "")
        return int(m.group(1)) if m else None

    def _compute_nights(
        self,
        new_ci: Optional[date],
        new_co: Optional[date],
        prev_nights: Optional[int],
    ) -> Optional[int]:
        if new_ci and new_co:
            return (new_co - new_ci).days
        return prev_nights

    def _apply_policy(
        self,
        message: str,
        dates: List[date],
        duration_nights: Optional[int],
        prev_ci: Optional[date],
        prev_co: Optional[date],
        prev_nights: Optional[int],
    ) -> Tuple[Optional[date], Optional[date]]:

        # همان سیاست قبلی: تاریخ‌ها اولویت دارند؛ nights فقط وقتی مجبور باشیم
        if not dates:
            # فقط مدت (بدون تاریخ) -> مجبوریم anchor را از prev_ci بگیریم
            if duration_nights is not None and prev_ci is not None:
                return prev_ci, prev_ci + timedelta(days=duration_nights)
            return prev_ci, prev_co

        has_in = bool(self.CHECK_IN_HINT.search(message))
        has_out = bool(self.CHECK_OUT_HINT.search(message))
        has_range = bool(self.RANGE_HINT.search(message))

        # اگر حداقل دو تاریخ داریم -> هر دو
        if len(dates) >= 2:
            return dates[0], dates[1]

        # یک تاریخ داریم
        d0 = dates[0]

        # فقط خروج
        if has_out:
            return prev_ci, d0

        # فقط ورود
        if has_in:
            if prev_nights is not None:
                return d0, d0 + timedelta(days=prev_nights)
            return d0, None

        # بازه گفته شده ولی فقط یک تاریخ داریم
        if has_range:
            if duration_nights is not None:
                return d0, d0 + timedelta(days=duration_nights)
            if prev_nights is not None:
                return d0, d0 + timedelta(days=prev_nights)
            return d0, None

        # تاریخ + مدت (بدون اشاره ورود/خروج) -> مجبوریم nights را استفاده کنیم
        if duration_nights is not None:
            return d0, d0 + timedelta(days=duration_nights)

        # fallback: یک تاریخ -> ورود، خروج قبلی (مثل قبل)
        return d0, prev_co
