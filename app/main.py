from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

from app.storage.repair import repair_missing_tables

from app.routers.text_to_voice.router import router as text_to_voice_router
from app.routers.voice_to_text.router import router as voice_to_text_router
from app.routers.ai_agent.router import router as ai_agent_router
from app.routers.show_database import router as show_database_router

repair_missing_tables()

app = FastAPI(redirect_slashes=False)
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "status": exc.status,
            "message": exc.message,
            "data": exc.data,
            "detail": exc.detail,
        },
    )
app.include_router(text_to_voice_router)
app.include_router(voice_to_text_router)
app.include_router(ai_agent_router)
app.include_router(show_database_router)