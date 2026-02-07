"""
Utility script to generate a PBKDF2-HMAC-SHA256 password hash for the admin account.
Usage: python generate_hash.py YOUR_PASSWORD
Or run inside Docker: docker compose exec backend python generate_hash.py YOUR_PASSWORD
"""

import hashlib
import os
import sys

PBKDF2_ITERATIONS = 600_000

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_hash.py YOUR_PASSWORD")
        sys.exit(1)

    password = sys.argv[1]
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    hashed = f"{salt.hex()}:{h.hex()}"
    print(f"\nGenerated PBKDF2 hash:\n{hashed}")
    print(f"\nAdd this to your .env file:")
    print(f"ADMIN_PASSWORD_HASH={hashed}")
