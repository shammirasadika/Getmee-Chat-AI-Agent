from app.clients.postgres_client import PostgresClient
from app.core.config import settings

class FeedbackService:
    def __init__(self):
        self.db = PostgresClient(settings.POSTGRES_URL)

    async def save_feedback(self, feedback_data: dict):
        await self.db.save_feedback(feedback_data)
