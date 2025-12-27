
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional


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
