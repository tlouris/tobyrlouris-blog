from pydantic import BaseModel, EmailStr, Field


class CommentCreate(BaseModel):
    post_id: str = Field(..., max_length=50)
    author: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    content: str = Field(..., min_length=1, max_length=2000)
