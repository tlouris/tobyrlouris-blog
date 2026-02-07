from pydantic import BaseModel
from typing import Optional


class BlogPostResponse(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: str
    category: str
    author: str
    reading_time: str
    image: Optional[str] = None
    date: str
    featured: bool

    class Config:
        from_attributes = True


class AdminPostCreate(BaseModel):
    title: str
    excerpt: str
    content: str
    category: str
    author: str = "Toby R. Louris"
    status: str = "draft"
    featured: bool = False
    reading_time: Optional[str] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None


class AdminPostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    featured: Optional[bool] = None
    reading_time: Optional[str] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None


class AdminPostStatusUpdate(BaseModel):
    status: str
