"""
Admin contact submission management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.contact import ContactSubmission
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/contacts", tags=["admin-contacts"])


@router.get("")
def list_contacts(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """List all contact submissions."""
    query = db.query(ContactSubmission)

    if status == "unread":
        query = query.filter(ContactSubmission.is_read == False)
    elif status == "read":
        query = query.filter(ContactSubmission.is_read == True)

    total = query.count()
    contacts = query.order_by(ContactSubmission.submitted_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "organization": c.organization,
                "topic": c.topic,
                "message": c.message,
                "is_read": c.is_read,
                "submitted_at": c.submitted_at.isoformat() if c.submitted_at else None
            }
            for c in contacts
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


@router.get("/{contact_id}")
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Get a single contact submission."""
    contact = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    return {
        "id": contact.id,
        "name": contact.name,
        "email": contact.email,
        "organization": contact.organization,
        "topic": contact.topic,
        "message": contact.message,
        "is_read": contact.is_read,
        "submitted_at": contact.submitted_at.isoformat() if contact.submitted_at else None
    }


@router.patch("/{contact_id}/read")
def mark_as_read(
    contact_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Mark a contact submission as read."""
    contact = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    contact.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.patch("/{contact_id}/unread")
def mark_as_unread(
    contact_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Mark a contact submission as unread."""
    contact = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    contact.is_read = False
    db.commit()
    return {"message": "Marked as unread"}


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Delete a contact submission."""
    contact = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact submission deleted"}
