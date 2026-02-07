"""
FastAPI Backend for Technology Innovations Blog
App factory: creates the app, registers middleware, and includes all routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from database import Base, engine, SessionLocal
from auth.session import cleanup_expired_sessions

import models  # noqa: F401 — registers all SQLAlchemy models with Base

from routers.public import router as public_router
from routers.admin_auth import router as admin_auth_router
from routers.admin_dashboard import router as admin_dashboard_router
from routers.admin_posts import router as admin_posts_router
from routers.admin_comments import router as admin_comments_router
from routers.admin_contacts import router as admin_contacts_router
from routers.admin_newsletter import router as admin_newsletter_router
from routers.admin_visitors import router as admin_visitors_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and clean up expired sessions
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cleanup_expired_sessions(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Technology Innovations Blog API",
    description="Backend API for wastewater technology blog",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=bool(ALLOWED_ORIGINS),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Cookie"],
)

# Public routes
app.include_router(public_router)

# Admin routes
app.include_router(admin_auth_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_posts_router)
app.include_router(admin_comments_router)
app.include_router(admin_contacts_router)
app.include_router(admin_newsletter_router)
app.include_router(admin_visitors_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
