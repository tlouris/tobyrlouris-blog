"""
Admin dashboard endpoints: stats and visitor analytics.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from database import get_db
from models.blog_post import BlogPost
from models.visitor_log import VisitorLog
from models.comment import Comment
from models.newsletter import NewsletterSubscriber
from models.contact import ContactSubmission
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin
from schemas.admin import DashboardStats, VisitorStatsResponse, VisitorDayData

router = APIRouter(prefix="/api/admin/dashboard", tags=["admin-dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Get aggregate counts for the dashboard."""
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    total_posts = db.query(func.count(BlogPost.id)).scalar()
    published_posts = db.query(func.count(BlogPost.id)).filter(BlogPost.status == "published").scalar()
    draft_posts = db.query(func.count(BlogPost.id)).filter(BlogPost.status == "draft").scalar()
    archived_posts = db.query(func.count(BlogPost.id)).filter(BlogPost.status == "archived").scalar()

    total_visitors_7d = db.query(func.count(VisitorLog.id)).filter(
        VisitorLog.timestamp >= seven_days_ago
    ).scalar()
    total_visitors_30d = db.query(func.count(VisitorLog.id)).filter(
        VisitorLog.timestamp >= thirty_days_ago
    ).scalar()

    pending_comments = db.query(func.count(Comment.id)).filter(Comment.approved == False).scalar()
    total_comments = db.query(func.count(Comment.id)).scalar()

    total_subscribers = db.query(func.count(NewsletterSubscriber.id)).scalar()
    active_subscribers = db.query(func.count(NewsletterSubscriber.id)).filter(
        NewsletterSubscriber.active == True
    ).scalar()

    unread_contacts = db.query(func.count(ContactSubmission.id)).filter(
        ContactSubmission.is_read == False
    ).scalar()

    return DashboardStats(
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        archived_posts=archived_posts,
        total_visitors_7d=total_visitors_7d,
        total_visitors_30d=total_visitors_30d,
        pending_comments=pending_comments,
        total_comments=total_comments,
        total_subscribers=total_subscribers,
        active_subscribers=active_subscribers,
        unread_contacts=unread_contacts
    )


@router.get("/visitors", response_model=VisitorStatsResponse)
def get_visitor_stats(
    period: str = "7d",
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Get daily visitor counts for chart data."""
    days = 7 if period == "7d" else 30
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        cast(VisitorLog.timestamp, Date).label("date"),
        func.count(VisitorLog.id).label("visitors")
    ).filter(
        VisitorLog.timestamp >= start_date
    ).group_by(
        cast(VisitorLog.timestamp, Date)
    ).order_by(
        cast(VisitorLog.timestamp, Date)
    ).all()

    result_map = {str(r.date): r.visitors for r in results}

    data = []
    for i in range(days):
        day = (start_date + timedelta(days=i + 1)).date()
        data.append(VisitorDayData(
            date=str(day),
            visitors=result_map.get(str(day), 0)
        ))

    return VisitorStatsResponse(period=period, data=data)
