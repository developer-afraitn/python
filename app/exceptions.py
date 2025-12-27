from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AppError(Exception):
    """
    Generic application-level exception usable across the whole project.
    - code: machine-readable error code
    - message: human-readable error message (safe to show to user if you want)
    - status_code: suggested HTTP status (FastAPI handler can use it)
    - details: extra info for debugging/clients
    """
    code: str = "APP_ERROR"
    message: str = "An application error occurred."
    status_code: int = 400
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
