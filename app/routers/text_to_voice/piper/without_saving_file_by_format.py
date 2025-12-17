from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.tts.piper_without_saving_file_by_format import PiperWithoutSavingFileByFormat

router = APIRouter()
svc = PiperWithoutSavingFileByFormat()


class TTSByFormatRequest(BaseModel):
    text: str
    lang: str = "fa"
    model_type: str = ""
    speed: float = 1.0
    bitrate: str = "64k"


@router.post("/without-saving-file-by-format")
def without_saving_file_by_format(body: TTSByFormatRequest):
    ogg_bytes = svc.synthesize_ogg(
        text=body.text,
        select_lang=body.lang,
        select_model_type=body.model_type,
        speed=body.speed,
        bitrate=body.bitrate,
    )

    return StreamingResponse(
        iter([ogg_bytes]),
        media_type="audio/ogg",
        headers={"Content-Disposition": "inline; filename=tts.ogg"},
    )
