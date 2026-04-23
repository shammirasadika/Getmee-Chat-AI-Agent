"""
FeedbackService — handles both response-level (message) feedback
and end-of-chat session ratings.

- Satisfied / Not Satisfied → message_feedback table
- 1–5 star rating + comment → session_feedback table
"""

import uuid
from typing import Optional
from app.clients.postgres_client import PostgresClient
from app.services.redis_session_service import RedisSessionService
from app.core.config import settings


class FeedbackService:
    def __init__(self):
        from app.clients.db_factory import get_db_client
        self.db = get_db_client()
        self.redis_session = RedisSessionService(settings.REDIS_URL)

    # ──────────────────────────────────────────────
    # Response-level feedback  (satisfied / not_satisfied)
    # ──────────────────────────────────────────────

    async def submit_message_feedback(self, session_key: str, session_id,
                                       message_id, feedback: str) -> dict:
        """
        Record response-level feedback.
        - feedback should be 'satisfied' or 'not_satisfied'
        - Updates Redis feedback_state and session context
        - If not_satisfied, sets up support_state for escalation flow
        """

        row = await self.db.insert_message_feedback(
            message_id=message_id,
            session_id=session_id,
            feedback=feedback,
        )
        # ...existing code...

        # Update Redis: mark feedback submitted
        await self.redis_session.mark_feedback_submitted(session_key)
        await self.redis_session.update_context(session_key, waiting_for_feedback=False)

        # If not satisfied, prepare escalation state
        if feedback == "not_satisfied":
            await self.redis_session.set_support_state(
                session_key,
                not_satisfied_selected=True,
                support_confirmation_pending=True,
                selected_message_id=str(message_id),
            )
            await self.redis_session.update_context(
                session_key, waiting_for_support_confirmation=True,
            )

        return row

    # ──────────────────────────────────────────────
    # Session-level feedback  (end-of-chat rating)
    # ──────────────────────────────────────────────

    async def submit_session_feedback(self, session_key: str, session_id,
                                       rating: int,
                                       comment: Optional[str] = None) -> dict:
        """
        Record a final 1–5 rating for the whole conversation.
        Updates Redis endchat_state and optionally expires session keys.
        """
        row = await self.db.insert_session_feedback(
            session_id=session_id,
            rating=rating,
            comment=comment,
        )
        # ...existing code...
        # Clear the pending flag
        await self.redis_session.set_endchat_state(
            session_key, chat_ended=True, session_feedback_pending=False,
        )
        await self.redis_session.update_context(
            session_key, session_feedback_pending=False,
        )
        # Expire session keys after a short grace period (5 min)
        await self.redis_session.expire_session(session_key, ttl=300)
        return row

    # ──────────────────────────────────────────────
    # Legacy helper  (kept for backwards-compat)
    # ──────────────────────────────────────────────

    async def save_feedback(self, feedback_data: dict):
        """Legacy: save to old feedback table."""
        await self.db.save_feedback(feedback_data)

    async def handle_feedback(self, request):
        """Legacy endpoint handler — writes to old feedback table."""
        from app.models.feedback import FeedbackResponse
        feedback_data = request.dict() if hasattr(request, 'dict') else dict(request)
        try:
            await self.save_feedback(feedback_data)
            return FeedbackResponse(success=True, detail="Feedback saved successfully.")
        except Exception as e:
            return FeedbackResponse(success=False, detail=f"Failed to save feedback: {e}")
