# GamerZone Backend

FastAPI backend for the GamerZone community website.

## Local setup

**1. Start PostgreSQL, Redis and Mailpit** (from the repository root, needs Docker
Desktop running):

```bash
docker compose up -d
```

Mailpit is a fake SMTP server for development: the app sends mail to it exactly as it
would to a real provider, but nothing leaves your machine. Read what was "sent" at
**http://localhost:8025** — that's where verification links appear.

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

## Tests

```bash
pytest
```

With a coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

The suite needs the Docker services running, because it exercises real PostgreSQL and
real Redis rather than substitutes — the app depends on Postgres behaviour (`timestamptz`,
`SERIAL`, unique constraints) that another engine would not reproduce.

Nothing touches development data:

- a separate `gamerzone_test` database is created automatically on first run, and every
  table is truncated between tests
- Redis database 15 is used instead of 0, and flushed around each test
- outgoing mail is captured in memory instead of being sent, so tests read verification
  and reset links straight out of the "inbox"

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
├── pyproject.toml      # pytest + coverage configuration
├── tests/              # pytest suite (fixtures live in conftest.py)
└── app/
    ├── main.py         # app instance, lifespan, CORS, middleware, handlers
    ├── api/
    │   ├── deps.py           # shared dependencies (session, current user, admin)
    │   ├── middleware.py     # request id + timing
    │   ├── error_handlers.py # one response shape for every failure
    │   └── v1/               # versioned routes
    ├── core/
    │   ├── config.py     # centralized settings (env-var driven)
    │   ├── security.py   # password hashing + JWT create/decode
    │   ├── tokens.py     # signed, expiring links (verification, reset)
    │   ├── exceptions.py # domain errors, free of HTTP concepts
    │   └── logging.py
    ├── db/
    │   ├── session.py  # async engine + per-request session dependency
    │   └── redis.py    # Redis client + revoked-token blacklist
    ├── models/         # SQLModel table + schema definitions
    └── services/       # business logic (users, mail)
    └── api/
        └── v1/         # versioned API routes
```
