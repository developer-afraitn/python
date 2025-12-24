from fastapi import FastAPI, HTTPException
import json
import asyncpg
import redis.asyncio as redis

from app.settings import settings
from app.routers.text_to_voice.router import router as text_to_voice_router
from app.routers.voice_to_text.router import router as voice_to_text_router
from app.routers.ai_agent.router import router as ai_agent_router
from app.logging_config import setup_logging
from app.config.db import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)
redis_client: redis.Redis | None = None
db_pool: asyncpg.Pool | None = None

app.include_router(text_to_voice_router)
app.include_router(voice_to_text_router)
app.include_router(ai_agent_router)
setup_logging()

@app.on_event("startup")
async def startup():
    global redis_client, db_pool

    # Redis
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    # Postgres pool
    db_pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)

    # Init table
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)


@app.on_event("shutdown")
async def shutdown():
    global redis_client, db_pool
    if redis_client:
        await redis_client.close()
    if db_pool:
        await db_pool.close()


@app.post("/users")
async def create_user(name: str):
    assert db_pool is not None
    assert redis_client is not None

    async with db_pool.acquire() as conn:
        user_id = await conn.fetchval(
            "INSERT INTO users(name) VALUES($1) RETURNING id;",
            name
        )

    # cache key را پاک/نو کن
    await redis_client.delete(f"user:{user_id}")

    return {"id": user_id, "name": name}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    assert db_pool is not None
    assert redis_client is not None

    cache_key = f"user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return {"source": "redis", **json.loads(cached)}

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, name FROM users WHERE id=$1;", user_id)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user = {"id": row["id"], "name": row["name"]}

    # 60 ثانیه کش
    await redis_client.setex(cache_key, 60, json.dumps(user))

    return {"source": "postgres", **user}