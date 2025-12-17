from fastapi import APIRouter
from app.routers.text_to_voice.piper.with_saving_file import router as with_saving_router
from app.routers.text_to_voice.piper.without_saving_file import router as without_saving_router
from app.routers.text_to_voice.piper.without_saving_file_by_format import router as by_format_router


router = APIRouter(prefix="/piper", tags=["text-to-voice", "piper"])

router.include_router(with_saving_router)
router.include_router(without_saving_router)
router.include_router(by_format_router)
