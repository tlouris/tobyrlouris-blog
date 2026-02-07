"""
FastAPI dependencies for admin authentication.
"""

from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.admin_session import AdminSession, LoginAttempt
from auth.session import validate_session
from config import ADMIN_SESSION_TIMEOUT_MINUTES


async def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminSession:
    """Dependency that validates the admin session cookie."""
    session_id = request.cookies.get("admin_session")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    admin_session = validate_session(db, session_id)
    if not admin_session:
        raise HTTPException(status_code=401, detail="Session expired")

    return admin_session


def check_rate_limit(ip_address: str, db: Session) -> bool:
    """Check if the IP has exceeded login attempt rate limits.
    Returns True if allowed, False if rate limited.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=15)
    recent_failures = db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == ip_address,
        LoginAttempt.attempted_at > cutoff,
        LoginAttempt.success == False
    ).count()
    return recent_failures < 5


def record_login_attempt(ip_address: str, success: bool, db: Session) -> None:
    """Record a login attempt for rate limiting."""
    attempt = LoginAttempt(
        ip_address=ip_address,
        success=success
    )
    db.add(attempt)
    db.commit()
