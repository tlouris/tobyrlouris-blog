"""
Password hashing and verification using bcrypt directly.
"""

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Used for initial setup."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
