import os
from fastapi import FastAPI
from routes.upload import router as upload_router
import uvicorn

app = FastAPI(title="Local Ingestion Pipeline")

# Register upload route
app.include_router(upload_router, prefix="/api")

if __name__ == "__main__":
    env = os.getenv("ENV", "development").lower()
    port = int(os.getenv("PORT", os.getenv("INGESTION_PORT", "8001")))
    reload_enabled = env == "development"

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_enabled)
