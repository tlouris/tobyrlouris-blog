from pydantic import BaseModel, Field
from typing import Optional


class VisitorLogCreate(BaseModel):
    page: str = Field(..., max_length=500)
    referrer: Optional[str] = Field("", max_length=1000)
    user_agent: str = Field(..., max_length=500)
    timestamp: str = Field(..., max_length=50)
