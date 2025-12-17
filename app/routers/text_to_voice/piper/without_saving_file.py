from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.tts.piper_without_saving import PiperTTSService

router = APIRouter()
tts_service = PiperTTSService()


class TTSRequest(BaseModel):
    text: str
    lang: str = "fa"
    model_type: str = ""
    speed: float = 1.0


@router.post("/without-saving-file")
def text_to_voice(body: TTSRequest):
    audio_bytes = tts_service.synthesize(
        text=body.text,
        select_lang=body.lang,
        select_model_type=body.model_type,
        speed=body.speed,
    )

    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "inline; filename=output.wav"
        },
    )
