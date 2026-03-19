from pydantic import BaseModel
from typing import Optional

class EscalationRequest(BaseModel):
    session_id: str
    message: str
    reason: Optional[str]

class EscalationResponse(BaseModel):
    escalated: bool
    detail: Optional[str]
