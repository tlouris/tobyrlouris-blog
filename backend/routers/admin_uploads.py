"""
Admin image upload endpoint.
"""

import os
import time
import secrets
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from models.admin_session import AdminSession
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/uploads", tags=["admin-uploads"])

UPLOAD_DIR = "/app/uploads/images"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    admin: AdminSession = Depends(get_current_admin),
):
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: JPEG, PNG, GIF, WebP.",
        )

    # Read file and check size
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10 MB.")

    # Generate unique filename
    ext = ALLOWED_TYPES[file.content_type]
    # Sanitize original name: keep only alphanumeric, hyphens, underscores
    original = os.path.splitext(file.filename or "upload")[0]
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in original)[:50]
    unique_name = f"{int(time.time())}_{secrets.token_hex(4)}_{safe_name}{ext}"

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Write file
    filepath = os.path.join(UPLOAD_DIR, unique_name)
    with open(filepath, "wb") as f:
        f.write(data)

    return {"url": f"/uploads/images/{unique_name}"}
