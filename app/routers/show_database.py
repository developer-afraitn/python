from __future__ import annotations
from fastapi import APIRouter
from fastapi import Query
from app.storage.repo.memoryRepo import MemoryRepo
from app.storage.repo.messageHistoryRepo import MessageHistoryRepo

router = APIRouter()
memory_repo = MemoryRepo()
message_history_repo = MessageHistoryRepo()

@router.get("/db/message_history")
def message_history(page: int = Query(1, ge=1)):
        return message_history_repo.list(page)


@router.get("/db/memory")
def message_history(page: int = Query(1, ge=1)):
        return memory_repo.list(page)