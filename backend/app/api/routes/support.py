from fastapi import APIRouter, HTTPException, Query
import traceback
from app.services.support_service import SupportService
from app.services.session_service import SessionService
from app.models.common import SupportSubmitRequest, SupportSubmitResponse

router = APIRouter()
support_service = SupportService()
session_service = SessionService()


@router.post("/", response_model=SupportSubmitResponse)
async def submit_support_request(request: SupportSubmitRequest):
    """Submit a support request after user provides their email."""
    try:
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

        result = await support_service.handle_fallback_escalation(
            session_id=request.session_id,
            user_message=request.user_message,
            user_email=request.user_email,
            language=request.language,
            fallback_message=fallback_message,
            chat_summary=chat_summary,
            source=request.source or "rag_fallback",
        )
        # Multilingual support: use STATIC_RESPONSES for success message
        from app.services.chat_service import STATIC_RESPONSES
        lang = (request.language or 'en').lower()
        if lang not in STATIC_RESPONSES:
            lang = 'en'
        # Use the Spanish or English equivalent of the success message
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
