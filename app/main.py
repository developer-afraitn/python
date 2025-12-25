from fastapi import FastAPI
from app.storage.repair import repair_missing_tables

from app.routers.text_to_voice.router import router as text_to_voice_router
from app.routers.voice_to_text.router import router as voice_to_text_router
from app.routers.ai_agent.router import router as ai_agent_router

repair_missing_tables()

app = FastAPI()

app.include_router(text_to_voice_router)
app.include_router(voice_to_text_router)
app.include_router(ai_agent_router)