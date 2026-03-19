from fastapi import APIRouter, status

from app.clients.redis_client import RedisClient
from app.clients.postgres_client import PostgresClient
from app.clients.chroma_client import ChromaClient
from app.core.config import settings

router = APIRouter()

@router.get("/", tags=["health"])
async def health_check():
    return {"status": "ok"}

@router.get("/ready", tags=["health"])
async def ready_check():
    # Optionally add checks for ChromaDB, Redis, DB
    return {"ready": True}

@router.get("/db-check", tags=["health"], status_code=status.HTTP_200_OK)
async def db_check():
    # Check Redis
    try:
        redis_client = RedisClient(settings.REDIS_URL)
        await redis_client.save_session("healthcheck", {"ping": "pong"})
        redis_ok = True
    except Exception:
        redis_ok = False

    # Check PostgreSQL
    try:
        pg_client = PostgresClient(settings.POSTGRES_URL)
        await pg_client.connect()
        async with pg_client.pool.acquire() as conn:
            await conn.execute("SELECT 1;")
        postgres_ok = True
    except Exception:
        postgres_ok = False

    # Check ChromaDB
    try:
        chroma_client = ChromaClient()
        # Try to list collections or get a collection (minimal check)
        _ = chroma_client.client.list_collections()
        chroma_ok = True
    except Exception:
        chroma_ok = False

    return {
        "redis": "ok" if redis_ok else "error",
        "postgres": "ok" if postgres_ok else "error",
        "chroma": "ok" if chroma_ok else "error"
    }
