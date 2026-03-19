from fastapi import APIRouter, Depends
from models.chat_model import ChatRequest, ChatResponse
from services.chat_service import ChatService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(ChatService)
):
    return service.process_message(request)