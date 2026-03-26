"""
MessageService — save and retrieve chat messages in PostgreSQL
and keep Redis recent-messages list in sync.
"""

from typing import Optional
from app.clients.postgres_client import PostgresClient
from app.services.redis_session_service import RedisSessionService
from app.core.config import settings


class MessageService:
    def __init__(self):
        self.db = PostgresClient(settings.POSTGRES_URL)
        self.redis_session = RedisSessionService(settings.REDIS_URL)

    async def save_user_message(self, session_id, session_key: str,
                                text: str, language: Optional[str] = None) -> dict:
        """Persist a user message and push to Redis recent-messages."""
        row = await self.db.insert_message(
            session_id=session_id,
            message_type="user",
            message_text=text,
            language=language,
        )
        # Push to Redis for context window
        await self.redis_session.push_message(session_key, {
            "role": "user",
            "text": text,
            "message_id": str(row["id"]),
        })
        return row

    async def save_bot_message(self, session_id, session_key: str,
                               text: str, language: Optional[str] = None,
                               fallback_used: bool = False,
                               source_type: Optional[str] = None) -> dict:
        """Persist a bot message, push to Redis, and set feedback_state."""
        row = await self.db.insert_message(
            session_id=session_id,
            message_type="bot",
            message_text=text,
            language=language,
            fallback_used=fallback_used,
            source_type=source_type,
        )
        msg_id = str(row["id"])
        # Push to Redis for context window
        await self.redis_session.push_message(session_key, {
            "role": "bot",
            "text": text,
            "message_id": msg_id,
        })
        # Set feedback state: waiting for user to rate this answer
        await self.redis_session.set_feedback_state(
            session_key, last_bot_message_id=msg_id,
            feedback_required=True, feedback_submitted=False,
        )
        # Mark session as waiting for feedback
        await self.redis_session.update_context(session_key, waiting_for_feedback=True)
        return row
