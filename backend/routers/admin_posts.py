"""
Admin blog post CRUD endpoints.
"""

import re
from unicodedata import normalize
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.blog_post import BlogPost
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin
from schemas.blog_post import AdminPostCreate, AdminPostUpdate, AdminPostStatusUpdate

router = APIRouter(prefix="/api/admin/posts", tags=["admin-posts"])


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from a title."""
    slug = normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


def ensure_unique_slug(db: Session, slug: str, exclude_id: int = None) -> str:
    """Ensure slug is unique, appending -2, -3, etc. if needed."""
    original_slug = slug
    counter = 2
    while True:
        query = db.query(BlogPost).filter(BlogPost.slug == slug)
        if exclude_id:
            query = query.filter(BlogPost.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{original_slug}-{counter}"
        counter += 1


@router.get("")
def list_posts(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """List all posts with optional filtering and pagination."""
    query = db.query(BlogPost)

    if status:
        query = query.filter(BlogPost.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (BlogPost.title.ilike(search_term)) | (BlogPost.excerpt.ilike(search_term))
        )

    total = query.count()
    posts = query.order_by(BlogPost.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "posts": [
            {
                "id": p.id,
                "slug": p.slug,
                "title": p.title,
                "excerpt": p.excerpt,
                "category": p.category,
                "author": p.author,
                "status": p.status,
                "featured": p.featured,
                "reading_time": p.reading_time,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in posts
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Get a single post by ID (includes full content)."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
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
        "status": post.status,
        "featured": post.featured,
        "reading_time": post.reading_time,
        "image_url": post.image_url,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None
    }


@router.post("")
def create_post(
    post_data: AdminPostCreate,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Create a new blog post."""
    slug = post_data.slug if post_data.slug else generate_slug(post_data.title)
    slug = ensure_unique_slug(db, slug)

    if post_data.status not in ("draft", "published", "archived"):
        raise HTTPException(status_code=400, detail="Invalid status")

    post = BlogPost(
        slug=slug,
        title=post_data.title,
        excerpt=post_data.excerpt,
        content=post_data.content,
        category=post_data.category,
        author=post_data.author,
        status=post_data.status,
        featured=post_data.featured,
        reading_time=post_data.reading_time,
        image_url=post_data.image_url
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"message": "Post created successfully", "id": post.id, "slug": post.slug}


@router.put("/{post_id}")
def update_post(
    post_id: int,
    post_data: AdminPostUpdate,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Update an existing blog post."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_fields = post_data.model_dump(exclude_unset=True)

    if "slug" in update_fields and update_fields["slug"]:
        update_fields["slug"] = ensure_unique_slug(db, update_fields["slug"], exclude_id=post_id)

    if "status" in update_fields and update_fields["status"] not in ("draft", "published", "archived"):
        raise HTTPException(status_code=400, detail="Invalid status")

    for field, value in update_fields.items():
        setattr(post, field, value)

    post.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Post updated successfully"}


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Delete a blog post."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


@router.patch("/{post_id}/status")
def update_post_status(
    post_id: int,
    status_update: AdminPostStatusUpdate,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Change a post's status (publish, draft, archive)."""
    if status_update.status not in ("draft", "published", "archived"):
        raise HTTPException(status_code=400, detail="Invalid status")

    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = status_update.status
    post.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Post status changed to {status_update.status}"}


@router.patch("/{post_id}/featured")
def toggle_featured(
    post_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Toggle a post's featured status."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.featured = not post.featured
    post.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Post featured status set to {post.featured}", "featured": post.featured}
