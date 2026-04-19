from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, feedback, health, support

app = FastAPI(
    title="GetMee Chatbot Backend",
    version="0.1.0",
    docs_url="/docs",         # Swagger UI
    redoc_url="/redoc",       # ReDoc UI
    openapi_url="/openapi.json"
)

# CORS configuration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    import os
    port = os.getenv("PORT", "8080")
    print(f"\nSwagger docs available at: http://localhost:{port}/docs\n")

    # Ensure PostgreSQL tables exist
    from app.core.config import settings
    from app.clients.postgres_client import PostgresClient
    try:
        pg = PostgresClient(settings.POSTGRES_URL)
        await pg.ensure_tables()
        print("[Startup] PostgreSQL tables ensured", flush=True)
    except Exception as e:
        print(f"[Startup] PostgreSQL table setup failed (non-blocking): {e}", flush=True)

@app.get("/")
def root():
    return {"message": "GetMee Chatbot Backend is running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
