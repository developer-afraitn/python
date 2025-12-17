from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tts.piper_with_saving import PiperTTSFileService

router = APIRouter()
tts_file_service = PiperTTSFileService()


class TTSFileRequest(BaseModel):
    text: str
    model_type: str = "amir"
    out_dir: str = "outputs"


@router.post("/with-saving-file")
def with_saving_file(body: TTSFileRequest):
    saved_path = tts_file_service.synthesize_to_file(
        text=body.text,
        model_type=body.model_type,
        out_dir=body.out_dir,
    )
    return {"saved_path": saved_path, "model_type": body.model_type}
