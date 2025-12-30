from fastapi import APIRouter
from app.routers.ai_agent.ai_agent import router as ai_agent_router

router = APIRouter(prefix="/ai-agent", tags=["ai-agent"])

router.include_router(ai_agent_router)