from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AppError(Exception):

    status: int = 500
    message: str = "An application error occurred."
    data: Dict[str, Any] = field(default_factory=dict)
    detail: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
