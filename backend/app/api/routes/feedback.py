from fastapi import APIRouter, Depends, HTTPException
from app.models.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
async def feedback_endpoint(request: FeedbackRequest, feedback_service: FeedbackService = Depends()):
    try:
        response = await feedback_service.handle_feedback(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
