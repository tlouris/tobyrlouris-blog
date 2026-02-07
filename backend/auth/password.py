"""
Password hashing and verification using PBKDF2-HMAC-SHA256 (stdlib).

Hash format: <32-char-hex-salt>:<64-char-hex-hash>
600,000 iterations per OWASP recommendation.
"""

import hashlib
import hmac
import os

PBKDF2_ITERATIONS = 600_000


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a PBKDF2 hash."""
    try:
        salt_hex, hash_hex = hashed_password.split(":")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    computed = hashlib.pbkdf2_hmac(
        "sha256", plain_password.encode(), salt, PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(computed, expected)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}:{h.hex()}"
