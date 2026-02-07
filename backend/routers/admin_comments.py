"""
Admin comment moderation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.comment import Comment
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/comments", tags=["admin-comments"])


@router.get("")
def list_comments(
    status: Optional[str] = None,
    post_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """List all comments with optional filtering."""
    query = db.query(Comment)

    if status == "pending":
        query = query.filter(Comment.approved == False)
    elif status == "approved":
        query = query.filter(Comment.approved == True)

    if post_id:
        query = query.filter(Comment.post_id == post_id)

    total = query.count()
    comments = query.order_by(Comment.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "comments": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "author": c.author,
                "email": c.email,
                "content": c.content,
                "approved": c.approved,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in comments
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


@router.patch("/{comment_id}/approve")
def approve_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Approve a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.approved = True
    db.commit()
    return {"message": "Comment approved"}


@router.patch("/{comment_id}/reject")
def reject_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Reject (unapprove) a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.approved = False
    db.commit()
    return {"message": "Comment rejected"}


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _session: AdminSession = Depends(get_current_admin)
):
    """Delete a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}
