from pydantic import BaseModel, EmailStr
from typing import Optional

class EscalationRequest(BaseModel):
    session_id: str
    message: str
    reason: Optional[str]

class EscalationResponse(BaseModel):
    escalated: bool
    detail: Optional[str]

class SupportSubmitRequest(BaseModel):
    session_id: str
    user_email: EmailStr
    user_message: str
    language: Optional[str] = "en"

class SupportSubmitResponse(BaseModel):
    success: bool
    message: str
    request_id: Optional[int] = None
