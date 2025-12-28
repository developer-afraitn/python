from __future__ import annotations
from typing import Any, Optional

def success_message(
    message: str,
    type: str = 'error',
    result: Any = {},
    request: Optional[Any] = [],
):
    return {
        "message": message,
        "type": type,
        "result": result,
        "request": request,
    }
