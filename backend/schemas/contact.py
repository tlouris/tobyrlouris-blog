from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    organization: Optional[str] = Field("", max_length=200)
    topic: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
