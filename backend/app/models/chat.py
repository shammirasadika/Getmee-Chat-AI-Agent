from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., example="How can I reset my password?")
    session_id: str = Field(..., example="abc123")
    language: Optional[str] = Field(None, example="en")

class ChatResponse(BaseModel):
    answer: str
    language: str
    sources: List[dict] = []
    fallback_used: bool = False
    requires_email: bool = False
    retrieval_language: Optional[str] = None
    message_id: Optional[str] = None
    session_uuid: Optional[str] = None       # PG chat_sessions.id (UUID)
    show_feedback: bool = True                # whether to show Satisfied/Not Satisfied
    show_support_options: bool = False        # whether to show Try Again / Contact Support
    prefilled_email: Optional[str] = None     # for direct email detection
    support_comment_enabled: Optional[bool] = None  # for direct email detection
