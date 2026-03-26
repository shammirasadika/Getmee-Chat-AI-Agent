from pydantic import BaseModel, Field
from typing import Optional


# ── Legacy (old feedback table) ──────────────────

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    feedback: str = Field(..., example="thumbs_up")
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    detail: Optional[str] = None


# ── Response-level message feedback ──────────────

class MessageFeedbackRequest(BaseModel):
    """Submitted when user clicks Satisfied / Not Satisfied on a bot answer."""
    session_key: str = Field(..., example="abc123")
    message_id: str = Field(..., example="uuid-of-bot-message")
    feedback: str = Field(..., example="satisfied")  # satisfied | not_satisfied

class MessageFeedbackResponse(BaseModel):
    success: bool
    feedback: str
    show_support_options: bool = False  # True when not_satisfied → offer Try Again / Contact Support
    detail: Optional[str] = None


# ── Session-level rating (end-of-chat) ───────────

class SessionFeedbackRequest(BaseModel):
    """Submitted when user rates the whole conversation at end of chat."""
    session_key: str = Field(..., example="abc123")
    rating: int = Field(..., ge=1, le=5, example=4)
    comment: Optional[str] = None

class SessionFeedbackResponse(BaseModel):
    success: bool
    detail: Optional[str] = None


# ── End-chat request ─────────────────────────────

class EndChatRequest(BaseModel):
    session_key: str = Field(..., example="abc123")

class EndChatResponse(BaseModel):
    success: bool
    show_session_feedback: bool = True
    detail: Optional[str] = None


# ── Support flow (Try Again / Contact Support) ───

class TryAgainRequest(BaseModel):
    session_key: str = Field(..., example="abc123")

class TryAgainResponse(BaseModel):
    success: bool
    detail: Optional[str] = None

class ContactSupportRequest(BaseModel):
    session_key: str = Field(..., example="abc123")
    user_email: Optional[str] = None
    issue_summary: Optional[str] = None  # auto-derived if empty

class ContactSupportResponse(BaseModel):
    success: bool
    ticket_id: Optional[str] = None
    detail: Optional[str] = None
