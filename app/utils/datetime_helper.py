
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional
import jdatetime

def to_date(value: Any) -> Optional[date]:
    """
    Convert value to datetime.date if possible.

    Accepts:
      - None -> None
      - date (but not datetime) -> same value
      - datetime -> value.date()
      - 'YYYY-MM-DD' string -> parsed to date
    Returns None if it can't parse.
    """
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        s = value.strip()
        try:
            return date.fromisoformat(s)  # accepts 'YYYY-MM-DD'
        except ValueError:
            return None

    return None


def to_iso_date_str(value: Any) -> Optional[str]:
    """
    Convert value to ISO 'YYYY-MM-DD' string if possible.
    Accepts date/datetime/'YYYY-MM-DD' string.
    Returns None if cannot convert.
    """
    d = to_date(value)
    return d.isoformat() if d else None


def today_date() -> date:
    """Return today's date (server local)."""
    return date.today()

PHP_TO_STRFTIME = {
    "l": "%A",  # weekday name
    "j": "%-d", # day of month (no leading zero) - روی ویندوز ممکنه کار نکنه
    "F": "%B",  # month name
    "Y": "%Y",  # year (4-digit)
    "H": "%H",  # hour 00-23
    "i": "%M",  # minute 00-59
    "s": "%S",  # second 00-59
}
def gregorian_to_jalali(gregorian: str, fmt: str) -> str:
    """
    gregorian:
      - 'YYYY-MM-DD'
      - 'YYYY-MM-DD HH:MM:SS'
    fmt: PHP-like (subset): l j F Y H:i:s  + escape with backslash like PHP
    """

    # اگر datetime بود → تبدیل به str
    if isinstance(gregorian, datetime):
        gregorian = gregorian.strftime("%Y-%m-%d %H:%M:%S")

    # اگر str بود → تمیزش کن
    if isinstance(gregorian, str):
        gregorian = gregorian.strip()



    g = gregorian.strip()
    if " " in g:
        gdt = datetime.fromisoformat(g)
    else:
        gdt = datetime.fromisoformat(g + " 00:00:00")

    jdt = jdatetime.datetime.fromgregorian(datetime=gdt)

    # تبدیل fmt از PHP tokens به strftime
    out = []
    esc = False
    for ch in fmt:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        out.append(PHP_TO_STRFTIME.get(ch, ch))

    strftime_fmt = "".join(out)

    # نکته: %-d روی لینوکس ok است. اگر ویندوز دارید، باید جایگزین کنیم.
    res = jdt.strftime(strftime_fmt)

    # اگر %-d پشتیبانی نشد، راه امن:
    # (در لینوکس لازم نیست، ولی برای سازگاری می‌تونی از این استفاده کنی)
    if "%-d" in strftime_fmt:
        try:
            res = jdt.strftime(strftime_fmt)
        except ValueError:
            # fallback: %d و حذف صفرهای اول
            res = jdt.strftime(strftime_fmt.replace("%-d", "%d")).replace(" 0", " ").lstrip("0")

    return res