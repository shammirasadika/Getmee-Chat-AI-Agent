from fastapi import FastAPI
from routes.upload import router as upload_router
import uvicorn

app = FastAPI(title="Local Ingestion Pipeline")

# Register upload route
app.include_router(upload_router, prefix="/api")

import webbrowser

if __name__ == "__main__":
    # Open Swagger UI automatically
    webbrowser.open("http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
