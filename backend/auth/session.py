"""
Server-side session management for admin authentication.
"""

import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.admin_session import AdminSession
from config import ADMIN_SESSION_TIMEOUT_MINUTES


def create_session(db: Session, ip_address: str, user_agent: str) -> AdminSession:
    """Create a new admin session and store it in the database."""
    session_id = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(minutes=ADMIN_SESSION_TIMEOUT_MINUTES)

    admin_session = AdminSession(
        id=session_id,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(admin_session)
    db.commit()
    db.refresh(admin_session)
    return admin_session


def validate_session(db: Session, session_id: str) -> AdminSession | None:
    """Validate a session ID and extend its expiry (sliding window)."""
    admin_session = db.query(AdminSession).filter(
        AdminSession.id == session_id,
        AdminSession.expires_at > datetime.utcnow()
    ).first()

    if admin_session:
        admin_session.expires_at = datetime.utcnow() + timedelta(minutes=ADMIN_SESSION_TIMEOUT_MINUTES)
        db.commit()

    return admin_session


def delete_session(db: Session, session_id: str) -> None:
    """Delete a session (logout)."""
    db.query(AdminSession).filter(AdminSession.id == session_id).delete()
    db.commit()


def cleanup_expired_sessions(db: Session) -> int:
    """Delete all expired sessions. Returns count of deleted rows."""
    count = db.query(AdminSession).filter(
        AdminSession.expires_at <= datetime.utcnow()
    ).delete()
    db.commit()
    return count
