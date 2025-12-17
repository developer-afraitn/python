from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.stt.google_stt import GoogleSTTService

router = APIRouter()
svc = GoogleSTTService()

class STTRequest(BaseModel):
    file_path: str = Field(..., description="Relative path under AUDIO_BASE_DIR")
    lang: str = "fa"

@router.post("/google/by-file-path")
def stt_google_by_file_path(body: STTRequest):
    return svc.transcribe_under_base(rel_path=body.file_path, lang=body.lang)
