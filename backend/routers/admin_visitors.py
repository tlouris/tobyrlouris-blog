"""
Admin visitor log review endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.visitor_log import VisitorLog
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/visitors", tags=["admin-visitors"])


@router.get("")
def list_visitors(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """List visitor logs with optional filtering."""
    query = db.query(VisitorLog)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(VisitorLog.timestamp >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)
            query = query.filter(VisitorLog.timestamp <= end)
        except ValueError:
            pass

    if page_filter:
        query = query.filter(VisitorLog.page.ilike(f"%{page_filter}%"))

    total = query.count()
    visitors = query.order_by(VisitorLog.timestamp.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "visitors": [
            {
                "id": v.id,
                "page": v.page,
                "referrer": v.referrer,
                "user_agent": v.user_agent,
                "ip_address": v.ip_address,
                "timestamp": v.timestamp.isoformat() if v.timestamp else None
            }
            for v in visitors
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }
