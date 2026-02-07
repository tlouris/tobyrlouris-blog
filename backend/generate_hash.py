"""
Utility script to generate a bcrypt password hash for the admin account.
Usage: python generate_hash.py YOUR_PASSWORD
Or run inside Docker: docker compose exec backend python generate_hash.py YOUR_PASSWORD
"""

import sys
import bcrypt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_hash.py YOUR_PASSWORD")
        sys.exit(1)

    password = sys.argv[1]
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"\nGenerated bcrypt hash:\n{hashed}")
    print(f"\nAdd this to your .env file:")
    print(f"ADMIN_PASSWORD_HASH={hashed}")
