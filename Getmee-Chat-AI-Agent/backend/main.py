from fastapi import FastAPI
from api.root import router as root_router
from api.chat import router as chat_router
from configuration.settings import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(root_router)
app.include_router(chat_router)