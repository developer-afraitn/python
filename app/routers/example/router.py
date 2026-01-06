from fastapi import APIRouter
from app.routers.example.example import router as example_router

router = APIRouter(prefix="/example", tags=["example"])

router.include_router(example_router)