from fastapi import APIRouter
from models.system_model import SystemStatusResponse
from services.system_service import get_system_status

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Welcome to GetMee Chat Backend"}

@router.get("/system-status", response_model=SystemStatusResponse)
def system_status():
    return get_system_status()