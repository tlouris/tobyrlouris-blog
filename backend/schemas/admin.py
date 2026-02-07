from pydantic import BaseModel
from typing import List, Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    expires_at: str


class SessionResponse(BaseModel):
    authenticated: bool
    expires_at: Optional[str] = None


class DashboardStats(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    archived_posts: int
    total_visitors_7d: int
    total_visitors_30d: int
    pending_comments: int
    total_comments: int
    total_subscribers: int
    active_subscribers: int
    unread_contacts: int


class VisitorDayData(BaseModel):
    date: str
    visitors: int


class VisitorStatsResponse(BaseModel):
    period: str
    data: List[VisitorDayData]
