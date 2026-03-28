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


# ── Legacy endpoint (backwards-compatible) ───────

@router.post("/", response_model=FeedbackResponse)
async def feedback_endpoint(request: FeedbackRequest, feedback_service: FeedbackService = Depends()):
    """Legacy: save quick thumbs-up/down to old feedback table."""
    try:
        response = await feedback_service.handle_feedback(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        await feedback_service.submit_session_feedback(
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

@router.post("/contact-support", response_model=ContactSupportResponse)
async def contact_support_endpoint(
    request: ContactSupportRequest,
    session_service: SessionService = Depends(),
    ticket_service: SupportTicketService = Depends(),
):
    """Create a support ticket after user confirms they want human help."""
    try:
        session = await session_service.get_or_create_session(request.session_key)
        session_id = session["id"]

        # Derive issue summary from Redis support_state if not provided
        issue_summary = request.issue_summary or "User requested human support after unsatisfactory bot answer."

        # Resolve related message_id from Redis support_state
        from app.services.redis_session_service import RedisSessionService
        from app.core.config import settings as _settings
        redis_svc = RedisSessionService(_settings.REDIS_URL)
        support_state = await redis_svc.get_support_state(request.session_key)
        message_id = None
        if support_state and support_state.get("selected_message_id"):
            try:
                message_id = _uuid.UUID(support_state["selected_message_id"])
            except ValueError:
                pass

        # Update user email on session if provided
        if request.user_email:
            from app.clients.postgres_client import PostgresClient
            db = PostgresClient(_settings.POSTGRES_URL)
            await db.update_session_email(session_id, request.user_email)

        # Save to support_requests for unified escalation tracking
        from app.services.support_service import SupportService
        support_service = SupportService()
        await support_service.handle_fallback_escalation(
            session_id=session_id,
            user_message=issue_summary,
            user_email=request.user_email or "",
            language="en",
            fallback_message=None,
            chat_summary=None,
            source=request.source or "user_unsatisfied",
        )
        ticket = await ticket_service.create_ticket(
            session_id=session_id,
            session_key=request.session_key,
            issue_summary=issue_summary,
            message_id=message_id,
            user_email=request.user_email,
        )
        return ContactSupportResponse(
            success=True,
            ticket_id=str(ticket["id"]),
            detail="Support ticket created. A team member will contact you.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
