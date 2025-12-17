from fastapi import APIRouter
from app.routers.voice_to_text.google_file_path import router as google_file_path_router

router = APIRouter(prefix="/voice-to-text", tags=["voice-to-text"])

router.include_router(google_file_path_router)