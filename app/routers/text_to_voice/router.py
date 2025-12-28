from fastapi import APIRouter
from app.routers.text_to_voice.piper.router import router as piper_router

router = APIRouter(prefix="/api/text-to-voice", tags=["text-to-voice"])

# زیرروترها
router.include_router(piper_router)
