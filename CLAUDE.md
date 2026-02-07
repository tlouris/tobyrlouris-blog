# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Start all services (nginx, backend, mariadb)
docker-compose up -d --build

# View logs (all services or specific)
docker-compose logs -f
docker-compose logs -f backend

# Restart a single service after changes
docker-compose restart backend

# Full rebuild (after dependency or Dockerfile changes)
docker-compose down && docker-compose up -d --build

# Access the database shell
docker-compose exec mysql mysql -u visitor_log_user -p visitor_log

# Generate admin password hash
python backend/generate_hash.py
```

There are no tests, linters, or formatters configured in this project.

## Architecture

Three Docker containers (docker-compose.yml): **nginx:alpine** serves static frontend and reverse-proxies `/api/` to **backend** (FastAPI/uvicorn on port 8000), which talks to **mariadb:10.11**.

### Backend (`backend/`)

Modular FastAPI application (Python 3.11, SQLAlchemy 2.0 ORM, PyMySQL driver):

- `main.py` — App factory: creates FastAPI app, registers CORS middleware, includes all routers. On startup, creates DB tables via `Base.metadata.create_all()` and cleans expired sessions.
- `config.py` — All settings loaded from environment variables via `python-dotenv`.
- `database.py` — SQLAlchemy engine, `SessionLocal` factory, `Base` declarative base, and `get_db` dependency.
- `models/` — SQLAlchemy models: `BlogPost`, `VisitorLog`, `Comment`, `ContactSubmission`, `NewsletterSubscriber`, `AdminSession`, `LoginAttempt`.
- `schemas/` — Pydantic v2 request/response models.
- `routers/public.py` — All public API endpoints (`/api/posts`, `/api/comments`, `/api/contact`, `/api/newsletter`, `/api/visitor-log`, `/api/health`).
- `routers/admin_*.py` — Admin CRUD endpoints under `/api/admin/` prefix. Each router handles one domain (posts, comments, contacts, newsletter, visitors, dashboard, auth).
- `auth/` — Session-based admin auth:
  - `password.py` — bcrypt verification via passlib.
  - `session.py` — Server-side sessions stored in DB with sliding-window expiry.
  - `dependencies.py` — `get_current_admin` FastAPI dependency validates `admin_session` httponly cookie.
  - `rate_limit.py` — In-memory IP-based rate limiter (sliding window) for public endpoints.

### Frontend (`frontend/`)

Vanilla HTML/CSS/JS, no build step. Served directly by nginx from `/usr/share/nginx/html`.

- Public pages: `index.html`, `blogs.html`, `about.html`, `contact.html`, `category.html`, `post.html`
- Admin panel: `frontend/admin/` — separate HTML pages (login, dashboard, post editor, comments, contacts, newsletter, visitors) with their own CSS/JS.

### Key conventions

- Blog posts use a `status` column (`published`/`draft`/`archived`), not a boolean.
- Admin auth is single-user: credentials come from env vars `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH` (bcrypt).
- Nginx config at `docker/nginx/conf.d/default.conf` — admin static files have cache disabled; regex location ordering matters (admin no-cache must come before general static caching rules).
- Database is seeded by `docker/mysql/init.sql` on first run.

## Environment Setup

Copy `backend/.env.example` to `.env` at project root. The `docker-compose.yml` uses `env_file: .env`.

**Gotcha**: `$` characters in bcrypt hashes get interpolated by docker-compose when set via `environment:` in the YAML. The project uses `env_file:` directive to avoid this.
