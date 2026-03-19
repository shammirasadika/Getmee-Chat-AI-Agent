from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, chat_service: ChatService = Depends()):
    try:
        response = await chat_service.handle_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
