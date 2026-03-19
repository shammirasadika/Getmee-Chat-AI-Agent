from pydantic import BaseModel, Field
from typing import Optional

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: Optional[str]
    feedback: str = Field(..., example="thumbs_up")
    comment: Optional[str]

class FeedbackResponse(BaseModel):
    success: bool
    detail: Optional[str]
