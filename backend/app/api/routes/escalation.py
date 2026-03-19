from fastapi import APIRouter, Depends, HTTPException
from app.models.common import EscalationRequest, EscalationResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/", response_model=EscalationResponse)
async def escalation_endpoint(request: EscalationRequest, chat_service: ChatService = Depends()):
    try:
        response = await chat_service.handle_escalation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
