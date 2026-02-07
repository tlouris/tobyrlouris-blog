"""
Application configuration loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://visitor_log_user:password@mysql:3306/visitor_log"
)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
ADMIN_SESSION_TIMEOUT_MINUTES = int(os.getenv("ADMIN_SESSION_TIMEOUT_MINUTES", "120"))
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
APP_ENV = os.getenv("APP_ENV", "production")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
]
