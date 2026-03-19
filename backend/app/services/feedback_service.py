from app.clients.postgres_client import PostgresClient
from app.core.config import settings

class FeedbackService:
    def __init__(self):
        self.db = PostgresClient(settings.POSTGRES_URL)

    async def save_feedback(self, feedback_data: dict):
        await self.db.save_feedback(feedback_data)

    async def handle_feedback(self, request):
        from app.models.feedback import FeedbackResponse
        feedback_data = request.dict() if hasattr(request, 'dict') else dict(request)
        try:
            await self.save_feedback(feedback_data)
            return FeedbackResponse(success=True, detail="Feedback saved successfully.")
        except Exception as e:
            return FeedbackResponse(success=False, detail=f"Failed to save feedback: {e}")
