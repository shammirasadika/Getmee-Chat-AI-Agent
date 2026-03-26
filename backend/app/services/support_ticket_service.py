"""
SupportTicketService — create and manage escalation tickets in PostgreSQL
and keep Redis support_state in sync.
"""

from typing import Optional
from app.clients.postgres_client import PostgresClient
from app.services.redis_session_service import RedisSessionService
from app.core.config import settings


class SupportTicketService:
    def __init__(self):
        self.db = PostgresClient(settings.POSTGRES_URL)
        self.redis_session = RedisSessionService(settings.REDIS_URL)

    async def create_ticket(self, session_id, session_key: str,
                            issue_summary: str,
                            message_id=None,
                            user_email: Optional[str] = None) -> dict:
        """
        Create a support ticket in PostgreSQL.
        Optionally mark the chat_session as escalated and clear Redis support_state.
        """
        ticket = await self.db.insert_support_ticket(
            session_id=session_id,
            issue_summary=issue_summary,
            message_id=message_id,
            user_email=user_email,
        )
        # Mark session as escalated
        await self.db.update_session_status(session_id, status="escalated")
        # Clear Redis escalation flags
        await self.redis_session.clear_support_state(session_key)
        await self.redis_session.update_context(
            session_key,
            waiting_for_support_confirmation=False,
            chat_status="escalated",
        )
        print(f"[SupportTicket] Created ticket {ticket['id']} for session {session_key}", flush=True)
        return ticket

    async def handle_try_again(self, session_key: str):
        """
        User chose 'Try Again' after not_satisfied — reset support state,
        keep session active.
        """
        await self.redis_session.clear_support_state(session_key)
        await self.redis_session.update_context(
            session_key,
            waiting_for_support_confirmation=False,
        )

    async def get_tickets(self, status: Optional[str] = None, limit: int = 50) -> list:
        return await self.db.get_support_tickets(status=status, limit=limit)
