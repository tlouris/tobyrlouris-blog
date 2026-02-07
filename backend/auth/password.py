"""
Password hashing and verification using passlib with bcrypt.
"""

from passlib.hash import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Used for initial setup."""
    return bcrypt.hash(password)
