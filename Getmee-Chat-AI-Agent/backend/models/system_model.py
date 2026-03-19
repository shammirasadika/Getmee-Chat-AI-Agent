from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    status: str