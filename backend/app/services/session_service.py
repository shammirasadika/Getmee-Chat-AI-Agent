"""
SessionService — manages chat session lifecycle.

- Creates / retrieves sessions in PostgreSQL (source of truth)
- Initializes Redis context for live session state
- Handles end-of-chat transitions
"""

from datetime import datetime, timezone
from typing import Optional
from app.clients.redis_client import RedisClient
from app.clients.postgres_client import PostgresClient
from app.services.redis_session_service import RedisSessionService
from app.core.config import settings


class SessionService:

    async def update_session_email(self, session_key: str, email: str):
        """Update the user_email for a session in the database."""
        session = await self.get_or_create_session(session_key)
        session_id = session["id"]
        await self.db.update_session_email(session_id, email)

    def __init__(self):
        from app.clients.db_factory import get_db_client
        self.redis = RedisClient(settings.REDIS_URL)
        self.db = get_db_client()
        self.redis_session = RedisSessionService(settings.REDIS_URL)

    # ──────────────────────────────────────────────
    # Session lifecycle
    # ──────────────────────────────────────────────

    async def get_or_create_session(self, session_key: str,
                                     language: Optional[str] = None) -> dict:
        """
        Ensure a chat_sessions row exists in PostgreSQL and Redis context
        is initialized. Returns the PG session row dict (with UUID id).
        """
        session = await self.db.get_or_create_session(session_key, language)
        # Initialize Redis context if not present
        ctx = await self.redis_session.get_context(session_key)
        if ctx is None:
            await self.redis_session.init_context(
                session_key, session_id=str(session["id"]), language=language or "en",
            )
        return session

    async def end_session(self, session_key: str, session_id) -> dict:
        """
        Mark a chat session as ended.
        - Updates PostgreSQL status + ended_at
        - Sets Redis endchat_state for session feedback prompt
        """
        now = datetime.now(timezone.utc)
        await self.db.update_session_status(session_id, status="ended", ended_at=now)
        await self.redis_session.set_endchat_state(
            session_key, chat_ended=True, session_feedback_pending=True,
        )
        await self.redis_session.update_context(
            session_key,
            active=False,
            chat_status="ended",
            session_feedback_pending=True,
        )
        return {"status": "ended", "ended_at": now.isoformat()}

    # ──────────────────────────────────────────────
    # Legacy helpers (used by existing chat_service)
    # ──────────────────────────────────────────────

    async def save_turn(self, session_id: str, turn: dict):
        """Legacy: append a conversation turn to Redis history."""
        await self.redis.save_session(session_id, turn)

    async def get_history(self, session_id: str):
        """Legacy: retrieve conversation turns from Redis."""
        return await self.redis.get_session(session_id)
