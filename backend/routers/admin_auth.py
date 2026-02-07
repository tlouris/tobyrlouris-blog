"""
Admin authentication endpoints: login, logout, session check.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session

from database import get_db
from schemas.admin import LoginRequest, LoginResponse, SessionResponse
from auth.password import verify_password
from auth.session import create_session, delete_session
from auth.dependencies import get_current_admin, check_rate_limit, record_login_attempt
from models.admin_session import AdminSession
from config import ADMIN_USERNAME, ADMIN_PASSWORD_HASH, APP_ENV

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])


@router.post("/login", response_model=LoginResponse)
def admin_login(
    login: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate admin and create a session."""
    ip_address = request.headers.get("X-Real-IP", request.client.host)

    if not check_rate_limit(ip_address, db):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again in 15 minutes."
        )

    if not ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Admin credentials not configured")

    if login.username != ADMIN_USERNAME or not verify_password(login.password, ADMIN_PASSWORD_HASH):
        record_login_attempt(ip_address, success=False, db=db)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    record_login_attempt(ip_address, success=True, db=db)

    user_agent = request.headers.get("User-Agent", "")
    admin_session = create_session(db, ip_address, user_agent)

    is_secure = request.headers.get("X-Forwarded-Proto", request.url.scheme) == "https"
    response.set_cookie(
        key="admin_session",
        value=admin_session.id,
        httponly=True,
        samesite="strict",
        secure=is_secure,
        path="/",
        max_age=admin_session.expires_at.timestamp() - admin_session.created_at.timestamp()
    )

    return LoginResponse(
        message="Login successful",
        expires_at=admin_session.expires_at.isoformat()
    )


@router.post("/logout")
def admin_logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    session: AdminSession = Depends(get_current_admin)
):
    """Destroy admin session and clear cookie."""
    delete_session(db, session.id)

    response.delete_cookie(key="admin_session", path="/")
    return {"message": "Logged out successfully"}


@router.get("/session", response_model=SessionResponse)
def check_session(session: AdminSession = Depends(get_current_admin)):
    """Check if the current session is valid."""
    return SessionResponse(
        authenticated=True,
        expires_at=session.expires_at.isoformat()
    )
