from app.clients.redis_client import RedisClient
from app.core.config import settings

class SessionService:
    def __init__(self):
        self.redis = RedisClient(settings.REDIS_URL)

    async def save_turn(self, session_id: str, turn: dict):
        await self.redis.save_session(session_id, turn)

    async def get_history(self, session_id: str):
        return await self.redis.get_session(session_id)
