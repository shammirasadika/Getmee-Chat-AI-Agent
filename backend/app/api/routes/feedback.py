"""
feedback.py

This module contains API endpoints for feedback-driven support escalation.
Use these endpoints when support escalation is triggered as part of the chat/feedback flow (e.g., user clicks 'Not Satisfied' and requests human help).

Best practice: Keep these endpoints separate from direct support requests for clarity, unless/until both flows are identical.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.feedback import (
    FeedbackRequest, FeedbackResponse,
    MessageFeedbackRequest, MessageFeedbackResponse,
    SessionFeedbackRequest, SessionFeedbackResponse,
    EndChatRequest, EndChatResponse,
    TryAgainRequest, TryAgainResponse,
    ContactSupportRequest, ContactSupportResponse,
)
from app.services.feedback_service import FeedbackService
from app.services.session_service import SessionService
from app.services.support_ticket_service import SupportTicketService
import uuid as _uuid

router = APIRouter()


# ── Message-level feedback  (Satisfied / Not Satisfied) ──

@router.post("/message", response_model=MessageFeedbackResponse)
async def message_feedback_endpoint(
    request: MessageFeedbackRequest,
    feedback_service: FeedbackService = Depends(),
    session_service: SessionService = Depends(),
):
    """
    Record Satisfied / Not Satisfied feedback for a specific bot message.
    If not_satisfied, response includes show_support_options=True so the
    frontend can present Try Again / Contact Support.
    """
    try:
        # Resolve PG session
        session = await session_service.get_or_create_session(request.session_key)
        session_id = session["id"]

        # Parse message UUID
        try:
            message_uuid = _uuid.UUID(request.message_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid message_id (must be UUID)")

        row = await feedback_service.submit_message_feedback(
            session_key=request.session_key,
            session_id=session_id,
            message_id=message_uuid,
            feedback=request.feedback,
        )
        return MessageFeedbackResponse(
            success=True,
            feedback=request.feedback,
            show_support_options=(request.feedback == "not_satisfied"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Session-level rating  (end-of-chat 1–5 stars) ──

@router.post("/session", response_model=SessionFeedbackResponse)
async def session_feedback_endpoint(
    request: SessionFeedbackRequest,
    feedback_service: FeedbackService = Depends(),
    session_service: SessionService = Depends(),
):
    """Record a 1–5 star rating for the whole conversation."""
    try:
        session = await session_service.get_or_create_session(request.session_key)
        session_id = session["id"]
        row = await feedback_service.submit_session_feedback(
            session_key=request.session_key,
            session_id=session_id,
            rating=request.rating,
            comment=request.comment,
        )
        return SessionFeedbackResponse(success=True, detail="Session rating saved.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── End Chat ─────────────────────────────────────

@router.post("/end-chat", response_model=EndChatResponse)
async def end_chat_endpoint(
    request: EndChatRequest,
    session_service: SessionService = Depends(),
):
    """Mark the chat as ended and signal that session feedback should be shown."""
    try:
        session = await session_service.get_or_create_session(request.session_key)
        session_id = session["id"]
        result = await session_service.end_session(request.session_key, session_id)
        return EndChatResponse(success=True, show_session_feedback=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Try Again  (after Not Satisfied) ─────────────

@router.post("/try-again", response_model=TryAgainResponse)
async def try_again_endpoint(
    request: TryAgainRequest,
    ticket_service: SupportTicketService = Depends(),
):
    """User chose Try Again after Not Satisfied — reset support state."""
    try:
        await ticket_service.handle_try_again(request.session_key)
        return TryAgainResponse(success=True, detail="You can ask your question again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Contact Human Support  (after Not Satisfied) ─

