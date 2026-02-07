"""
Admin newsletter subscriber management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.newsletter import NewsletterSubscriber
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/newsletter", tags=["admin-newsletter"])


@router.get("/subscribers")
def list_subscribers(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """List all newsletter subscribers."""
    query = db.query(NewsletterSubscriber)

    if status == "active":
        query = query.filter(NewsletterSubscriber.active == True)
    elif status == "inactive":
        query = query.filter(NewsletterSubscriber.active == False)

    total = query.count()
    subscribers = query.order_by(NewsletterSubscriber.subscribed_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "subscribers": [
            {
                "id": s.id,
                "email": s.email,
                "active": s.active,
                "subscribed_at": s.subscribed_at.isoformat() if s.subscribed_at else None
            }
            for s in subscribers
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


@router.patch("/subscribers/{subscriber_id}/deactivate")
def deactivate_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Deactivate a newsletter subscriber."""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    subscriber.active = False
    db.commit()
    return {"message": "Subscriber deactivated"}


@router.patch("/subscribers/{subscriber_id}/activate")
def activate_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Reactivate a newsletter subscriber."""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    subscriber.active = True
    db.commit()
    return {"message": "Subscriber activated"}


@router.delete("/subscribers/{subscriber_id}")
def remove_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Remove a newsletter subscriber."""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    db.delete(subscriber)
    db.commit()
    return {"message": "Subscriber removed"}
