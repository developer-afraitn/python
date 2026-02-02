from __future__ import annotations
from typing import Any, Optional
import time
from app.configs.state import history_info
from app.storage.repo.messageHistoryRepo import MessageHistoryRepo


def success_message(
    message: str,
    type: str = 'error',
    result: Any = {},
    request: Optional[Any] = [],
):

    duration_ms = int((time.time() - history_info['start_time']) * 1000)
    history_repo = MessageHistoryRepo()
    history_repo.update(id=history_info['id'],
                        updates={
                            "response": message,
                            "duration": duration_ms,
                        }
    )
    return {
        "message": message,
        "type": type,
        "result": result,
        "request": request,
    }
