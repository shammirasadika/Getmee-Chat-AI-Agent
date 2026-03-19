from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, feedback, escalation, health

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
app.include_router(escalation.router, prefix="/api/escalation", tags=["escalation"])
app.include_router(health.router, prefix="/api/health", tags=["health"])


@app.on_event("startup")
async def print_swagger_url():
    import os
    port = os.getenv("PORT", "8001")
    print(f"\nSwagger docs available at: http://localhost:{port}/docs\n")

@app.get("/")
def root():
    return {"message": "GetMee Chatbot Backend is running"}
