print("[DEBUG] Backend main.py loaded and running!", flush=True)

# Ensure .env is loaded for environment variables
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, feedback, health, support



import os
from app.core.config import settings

app = FastAPI(
    title="GetMee Chatbot Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration — reads from ALLOWED_ORIGINS env var

# Strict ENV-driven CORS configuration
origins_env = os.getenv("CORS_ALLOWED_ORIGINS")
if not origins_env:
    raise ValueError("CORS_ALLOWED_ORIGINS is not set in environment variables")
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
print(f"[CORS] Allowed origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(health.router, prefix="/api/health", tags=["health"])


@app.on_event("startup")
async def startup_event():
    import logging
    logger = logging.getLogger("startup")
    logger.info(f"Swagger docs available at: http://0.0.0.0:{settings.PORT}/docs")
    logger.info(f"CORS allowed origins: {settings.ALLOWED_ORIGINS}")
    logger.info(f"ChromaDB mode: {settings.CHROMA_MODE}")

    # Ensure PostgreSQL tables exist
    from app.clients.postgres_client import PostgresClient
    try:
        pg = PostgresClient(settings.POSTGRES_URL)
        await pg.ensure_tables()
        logger.info("PostgreSQL tables ensured")
    except Exception as e:
        logger.warning(f"PostgreSQL table setup failed (non-blocking): {e}")

@app.get("/")
def root():
    return {"message": "GetMee Chatbot Backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
