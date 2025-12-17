from fastapi import FastAPI
from app.config import settings
from app.routers.text_to_voice.router import router as text_to_voice_router
from app.routers.voice_to_text.router import router as voice_to_text_router

app = FastAPI()

app.include_router(text_to_voice_router)
app.include_router(voice_to_text_router)