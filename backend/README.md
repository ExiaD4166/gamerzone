# GamerZone Backend

FastAPI backend for the GamerZone community website.

## Local setup

**1. Start PostgreSQL and Redis** (from the repository root, needs Docker Desktop running):

```bash
docker compose up -d
```

**2. Install Python dependencies:**

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**3. Create your environment file** — copy `.env.example` to `.env` and make sure
`DATABASE_URL` matches the credentials in the root `.env` used by Docker Compose.

**4. Apply database migrations:**

```bash
alembic upgrade head
```

## Run the dev server

```bash
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

## Database migrations

The schema is owned by Alembic — the application never creates tables on startup.
After changing anything in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
```

Review the generated file in `alembic/versions/` (autogenerate is a helpful draft,
not a guarantee — it cannot detect renames, for example), then apply it:

```bash
alembic upgrade head
```

Useful commands: `alembic current` (where the DB is), `alembic history` (all
revisions), `alembic downgrade -1` (undo the last migration).

## Project structure

```
backend/
├── alembic/            # migration environment
│   └── versions/       # migration scripts (committed to git)
├── alembic.ini         # Alembic config (connection string comes from .env)
└── app/
    ├── main.py         # FastAPI app instance, lifespan, mounts routers
    ├── core/
    │   └── config.py   # centralized settings (env-var driven)
    ├── db/
    │   ├── session.py  # async engine + per-request session dependency
    │   └── redis.py    # Redis client + revoked-token blacklist
    ├── models/         # SQLModel table + schema definitions
    └── api/
        └── v1/         # versioned API routes
```
