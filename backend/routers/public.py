"""
Public API endpoints — migrated from the original main.py with no behavior changes.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from database import get_db, SessionLocal
from models.blog_post import BlogPost
from models.visitor_log import VisitorLog
from models.comment import Comment
from models.contact import ContactSubmission
from models.newsletter import NewsletterSubscriber
from schemas.blog_post import BlogPostResponse
from schemas.visitor import VisitorLogCreate
from schemas.contact import ContactSubmissionCreate
from schemas.comment import CommentCreate
from schemas.newsletter import NewsletterSubscribe
from auth.rate_limit import rate_limiter

router = APIRouter()


@router.get("/")
def read_root():
    return {
        "message": "Technology Innovations Blog API",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/api/health")
def health_check():
    """Health check endpoint"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.post("/api/visitor-log")
def log_visitor(visitor: VisitorLogCreate, request: Request, db: Session = Depends(get_db)):
    """Log website visitor"""
    rate_limiter.check(request, max_requests=60, window_seconds=60)
    try:
        ip_address = (
            request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.client.host
        )
        db_visitor = VisitorLog(
            page=visitor.page,
            referrer=visitor.referrer,
            user_agent=visitor.user_agent,
            ip_address=ip_address
        )
        db.add(db_visitor)
        db.commit()
        return {"message": "Visitor logged successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/contact")
def submit_contact(contact: ContactSubmissionCreate, request: Request, db: Session = Depends(get_db)):
    """Handle contact form submission"""
    rate_limiter.check(request, max_requests=5, window_seconds=300)
    try:
        db_contact = ContactSubmission(
            name=contact.name,
            email=contact.email,
            organization=contact.organization,
            topic=contact.topic,
            message=contact.message
        )
        db.add(db_contact)
        db.commit()
        return {"message": "Contact form submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/comments")
def submit_comment(comment: CommentCreate, request: Request, db: Session = Depends(get_db)):
    """Submit a blog comment (requires moderation)"""
    rate_limiter.check(request, max_requests=10, window_seconds=300)
    try:
        db_comment = Comment(
            post_id=comment.post_id,
            author=comment.author,
            email=comment.email,
            content=comment.content,
            approved=False
        )
        db.add(db_comment)
        db.commit()
        return {"message": "Comment submitted for moderation"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/comments")
def get_comments(post_id: str, db: Session = Depends(get_db)):
    """Get approved comments for a post"""
    try:
        comments = db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.approved == True
        ).order_by(Comment.created_at.desc()).all()

        return [
            {
                "id": c.id,
                "author": c.author,
                "content": c.content,
                "date": c.created_at.isoformat()
            }
            for c in comments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/newsletter")
def subscribe_newsletter(subscriber: NewsletterSubscribe, request: Request, db: Session = Depends(get_db)):
    """Subscribe to newsletter"""
    rate_limiter.check(request, max_requests=5, window_seconds=300)
    try:
        existing = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.email == subscriber.email
        ).first()

        if existing:
            if not existing.active:
                existing.active = True
                db.commit()
                return {"message": "Subscription reactivated"}
            return {"message": "Already subscribed"}

        db_subscriber = NewsletterSubscriber(email=subscriber.email)
        db.add(db_subscriber)
        db.commit()
        return {"message": "Successfully subscribed to newsletter"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/posts", response_model=List[BlogPostResponse])
def get_posts(
    category: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get blog posts"""
    try:
        query = db.query(BlogPost).filter(BlogPost.status == "published")

        if category:
            query = query.filter(BlogPost.category == category)

        query = query.order_by(BlogPost.created_at.desc())

        if limit:
            query = query.limit(limit)

        posts = query.all()

        return [
            BlogPostResponse(
                id=p.id,
                slug=p.slug,
                title=p.title,
                excerpt=p.excerpt,
                category=p.category,
                author=p.author,
                reading_time=p.reading_time or "5 min read",
                image=p.image_url,
                date=p.created_at.strftime("%Y-%m-%d"),
                featured=p.featured
            )
            for p in posts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/posts/featured", response_model=BlogPostResponse)
def get_featured_post(db: Session = Depends(get_db)):
    """Get featured blog post"""
    try:
        post = db.query(BlogPost).filter(
            BlogPost.featured == True,
            BlogPost.status == "published"
        ).first()

        if not post:
            post = db.query(BlogPost).filter(
                BlogPost.status == "published"
            ).order_by(BlogPost.created_at.desc()).first()

        if not post:
            raise HTTPException(status_code=404, detail="No posts found")

        return BlogPostResponse(
            id=post.id,
            slug=post.slug,
            title=post.title,
            excerpt=post.excerpt,
            category=post.category,
            author=post.author,
            reading_time=post.reading_time or "5 min read",
            image=post.image_url,
            date=post.created_at.strftime("%Y-%m-%d"),
            featured=post.featured
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/posts/{slug}")
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a single blog post by slug"""
    try:
        post = db.query(BlogPost).filter(
            BlogPost.slug == slug,
            BlogPost.status == "published"
        ).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return {
            "id": post.id,
            "slug": post.slug,
            "title": post.title,
            "excerpt": post.excerpt,
            "content": post.content,
            "category": post.category,
            "author": post.author,
            "reading_time": post.reading_time or "5 min read",
            "image": post.image_url,
            "date": post.created_at.strftime("%Y-%m-%d"),
            "featured": post.featured
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
