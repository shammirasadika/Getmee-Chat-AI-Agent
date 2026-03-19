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
