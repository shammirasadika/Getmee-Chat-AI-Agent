"""
support.py

This module contains API endpoints for direct support requests.
Use these endpoints when a user proactively submits a support request (e.g., via a standalone support form), not tied to the feedback flow.

Best practice: Keep these endpoints separate from feedback-driven escalation for clarity, unless/until both flows are identical.
"""
from fastapi import APIRouter, HTTPException, Query
import traceback
from datetime import datetime, timezone
from app.services.support_service import SupportService
from app.services.session_service import SessionService

from app.models.common import SupportSubmitRequest, SupportSubmitResponse
from app.services.chat_service import ChatService

router = APIRouter()
support_service = SupportService()
session_service = SessionService()
ticket_service = SupportTicketService()


@router.post("/", response_model=SupportSubmitResponse)
async def submit_support_request(request: SupportSubmitRequest):
    """Submit a support request after user provides their email."""
    try:
        # --- Redis-based support state tracking and repeat submission prevention ---
        redis_session = session_service.redis_session
        support_state = await redis_session.get_support_state(request.session_id)
        if support_state and support_state.get("support_request_sent"):
            # Already submitted, block repeat
            from app.services.chat_service import STATIC_RESPONSES
            lang = (request.language or 'en').lower()
            if lang not in STATIC_RESPONSES:
                lang = 'en'
            repeat_msg = {
                'en': "You have already submitted a support request for this session. Our team will contact you soon.",
                'es': "Ya has enviado una solicitud de soporte para esta sesión. Nuestro equipo te contactará pronto."
            }
            message = STATIC_RESPONSES[lang].get('support_repeat') \
                if 'support_repeat' in STATIC_RESPONSES[lang] else repeat_msg[lang]
            return SupportSubmitResponse(
                success=False,
                message=message,
                request_id=None,
            )

        # Build chat summary and extract fallback message from session history
        chat_summary = None
        fallback_message = None
        try:
            history = await session_service.get_history(request.session_id)
            if history:
                recent = history[-5:]
                chat_summary = "\n".join(
                    f"User: {t.get('user', '')}\nBot: {t.get('bot', '')}" for t in recent
                )
                # The last bot response is the fallback message
                if history:
                    fallback_message = history[-1].get("bot")
        except Exception as e:
            print(f"[Support] Failed to get chat summary: {e}", flush=True)


        # If the user_message is 'unsatisfied' or empty, try to use the last user message from chat history
        reported_issue = request.user_message
        if (not reported_issue or reported_issue.strip().lower() == 'unsatisfied') and history:
            # Find the last non-empty user message in history
            for msg in reversed(history):
                if msg.get('user') and msg.get('user').strip().lower() != 'unsatisfied':
                    reported_issue = msg.get('user')
                    break
        if not reported_issue:
            reported_issue = '(no issue provided)'


        # Prefer escalation_source from Redis session context, then request, then default
        context = await redis_session.get_context(request.session_id)
        source = None
        if context and context.get("escalation_source"):
            source = context["escalation_source"]
        elif hasattr(request, "escalation_source") and request.escalation_source:
            source = request.escalation_source
        else:
            source = "User direct request"

        # Do not override fallback escalation to direct escalation; fallback remains fallback

        result = await support_service.handle_fallback_escalation(
            session_id=request.session_id,
            user_message=reported_issue,
            user_email=request.user_email,
            language=request.language,
            fallback_message=fallback_message,
            chat_summary=chat_summary,
            source=source,
        )

        # Also create a support ticket in the new table
        from app.services.support_ticket_service import SupportTicketService
        ticket_service = SupportTicketService()
        # Look up the chat_sessions row by session_key to get the UUID id
        session_row = await session_service.get_or_create_session(request.session_id)
        uuid_session_id = session_row["id"]
        await ticket_service.create_ticket(
            session_id=uuid_session_id,
            session_key=request.session_id,
            issue_summary=reported_issue,
            message_id=None,
            user_email=request.user_email,
        )

        # --- INCREMENT SUPPORT REQUEST COUNT ONLY AFTER ACTUAL SUBMISSION ---
        chat_service = ChatService()
        # Debug: print support_request_count before
        context_before = await chat_service.message_service.redis_session.get_context(request.session_id)
        print(f"[Support] Before increment: support_request_count = {context_before.get('support_request_count', 0)} for session_key={request.session_id}", flush=True)
        await chat_service._mark_support_submitted(
            session_key=request.session_id,
            email=request.user_email,
            ticket_id=str(result.get("request_id")) if result.get("request_id") else None,
            status="open"
        )
        # Debug: print support_request_count after
        context_after = await chat_service.message_service.redis_session.get_context(request.session_id)
        print(f"[Support] After increment: support_request_count = {context_after.get('support_request_count', 0)} for session_key={request.session_id}", flush=True)

        # Set support state in Redis to prevent repeat submissions
        await redis_session.set_support_state(
            request.session_id,
            not_satisfied_selected=True,
            support_confirmation_pending=False,
            selected_message_id=None
        )
        # Mark support_request_sent flag
        await redis_session.update_context(request.session_id, support_request_sent=True, support_email=request.user_email)

        # Multilingual support: use STATIC_RESPONSES for success message
        from app.services.chat_service import STATIC_RESPONSES
        lang = (request.language or 'en').lower()
        if lang not in STATIC_RESPONSES:
            lang = 'en'
        support_success_msg = {
            'en': "Thank you! A team member will contact you soon.",
            'es': "¡Gracias! Un miembro del equipo te contactará pronto."
        }
        message = STATIC_RESPONSES[lang].get('email_success') \
            if 'email_success' in STATIC_RESPONSES[lang] else support_success_msg[lang]
        return SupportSubmitResponse(
            success=True,
            message=message,
            request_id=result.get("request_id"),
        )
    except Exception as e:
        print("[Support API] Exception in submit_support_request:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_support_requests(
    status: str = Query(None, description="Filter by status: pending, resolved, etc."),
    limit: int = Query(50, ge=1, le=200, description="Max results to return"),
):
    """Retrieve support requests from PostgreSQL."""
    try:
        requests = await support_service.get_requests(status=status, limit=limit)
        return {"count": len(requests), "requests": requests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets", response_model=CreateTicketResponse)
async def create_support_ticket(request: CreateTicketRequest):
    """Create a support ticket with session_id, email, and issue."""
    try:
        ticket = await ticket_service.create_ticket_direct(
            session_id=request.session_id,
            user_email=request.email,
            issue_summary=request.issue,
        )
        created_at = ticket.get("created_at", datetime.now(timezone.utc)).isoformat()
        return CreateTicketResponse(
            success=True,
            ticket_id=str(ticket["id"]),
            created_at=created_at,
            message="Support ticket created successfully. A team member will contact you.",
        )
    except Exception as e:
        print("[Support API] Exception in create_support_ticket:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
