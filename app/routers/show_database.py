from __future__ import annotations
from fastapi import APIRouter, Request , Query
from app.storage.repo.memoryRepo import MemoryRepo
from app.storage.repo.messageHistoryRepo import MessageHistoryRepo
from app.storage.repo.apiLogRepo import ApiLogRepo
from fastapi.templating import Jinja2Templates
import os

from app.utils.datetime_helper import gregorian_to_jalali
from app.utils.main_helper import shorten_string

router = APIRouter()
memory_repo = MemoryRepo()
message_history_repo = MessageHistoryRepo()
api_log_repo = ApiLogRepo()


templates = Jinja2Templates(directory="app/views")
templates.env.filters["gregorian_to_jalali"] = gregorian_to_jalali
templates.env.filters["shorten_string"] = shorten_string

@router.get("/")
def show_database(request: Request):
        return templates.TemplateResponse(
            "tables.html",
            {
                "request": request,
                "url_prefix": os.getenv("URL_PREFIX")
            }
        )

@router.get("/db/message_history")
def message_history(request: Request,page: int = Query(1, ge=1)):
        data = message_history_repo.list(page)
        return templates.TemplateResponse(
                "message_history.html",
                {
                    "request": request,
                    "data": data,
                    "page": page
                }
        )

@router.get("/db/memory")
def memory(request: Request,page: int = Query(1, ge=1)):

        data = memory_repo.list(page)
        return templates.TemplateResponse(
                "memory.html",
                {
                    "request": request,
                    "data": data,
                    "page": page
                }
        )

@router.get("/db/api_log")
def api_log(request: Request,page: int = Query(1, ge=1)):
        data = api_log_repo.list(page)
        return templates.TemplateResponse(
                "api_log.html",
                {
                    "request": request,
                    "data": data,
                    "page": page
                }
        )

from app.services.example.chromadb import ChromaDb
chromadb  = ChromaDb()
@router.get("/db/chromadb")
def chromadb(request: Request,page: int = Query(1, ge=1)):
    chromadb  = ChromaDb()
    return chromadb.get_all()