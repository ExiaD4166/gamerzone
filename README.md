# GamerZone

A gaming community website — homepage, about page, member profiles, and a members-only
download page for game and mod links. Built to practice an industry-style full-stack
workflow: layered architecture, real migrations, proper authentication, and tests.

**Feature-complete and running locally. Deployment is the next step — see
[DEPLOYMENT.md](DEPLOYMENT.md).**

---

## What it does

Members register with an email address, confirm it, and sign in to reach the download
links. Administrators curate those links. Everything is enforced server-side.

**Accounts and authentication**
- Registration with Argon2id password hashing
- Email confirmation via a signed, expiring link
- OAuth2 password flow issuing JWT access tokens
- Logout that genuinely revokes a token, using a Redis blacklist
- Password reset over single-use links that also sign the account out everywhere

**Access control** — four levels, strictly nested:

| Caller | Can read links | Can manage links |
|---|---|---|
| Anonymous | ✗ `401` | ✗ |
| Signed in, email unconfirmed | ✗ `403` | ✗ |
| Verified member | ✓ | ✗ `403` |
| Administrator | ✓ | ✓ |

**Operational**
- Every response carries an `X-Request-ID`, echoed in error bodies and the logs
- One error shape everywhere: `{detail, code, request_id}`
- Stack traces stay in the logs and never reach a client

## Stack

| | |
|---|---|
| **API** | FastAPI, Python 3.11, async throughout |
| **Database** | PostgreSQL 16 via SQLModel + SQLAlchemy (asyncpg), Alembic migrations |
| **Cache** | Redis 7 — revoked-token blacklist |
| **Auth** | OAuth2 password flow, JWT (PyJWT), Argon2id (pwdlib), itsdangerous for signed links |
| **Mail** | aiosmtplib; Mailpit locally so development never emails a real person |
| **Tests** | pytest + httpx — 56 tests, 93% coverage, ~10s |
| **Infra** | Docker Compose |
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind 4 |

## Architecture

Requests move through clearly separated layers, and each one only knows about the layer
below it:

```
  HTTP request
       │
   middleware ......... request id, timing, logging
       │
   router ............. HTTP concerns only: status codes, response models
       │
   dependencies ....... session, current user, verified user, admin
       │
   service ............ business rules; raises domain errors, knows nothing about HTTP
       │
   model / session .... SQLModel tables, async database session
       │
   PostgreSQL
```

Two consequences worth noting. Services raise domain exceptions rather than
`HTTPException`, so the same function works from a CLI or a background job — a single
handler translates them to responses. And response models act as a security boundary:
`UserRead` has no password field, so a hash cannot leak even if an endpoint returns a
full `User`.

## Running it

Requires Docker Desktop and Python 3.11+.

```bash
docker compose up -d
```

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

| | |
|---|---|
| API docs (Swagger) | http://127.0.0.1:8000/docs |
| Mail inbox (Mailpit) | http://localhost:8025 |

Tests:

```bash
cd backend && pytest
```

The frontend runs independently — the home page needs no API:

```bash
cd frontend
npm install
npm run dev
```

Full backend detail — migrations, test isolation, project layout — is in
[`backend/README.md`](backend/README.md).

## API

| Method | Path | Access |
|---|---|---|
| `POST` | `/api/v1/auth/signup` | public |
| `POST` | `/api/v1/auth/login` | public |
| `GET` | `/api/v1/auth/verify` | public (link from email) |
| `POST` | `/api/v1/auth/resend-verification` | public |
| `POST` | `/api/v1/auth/forgot-password` | public |
| `POST` | `/api/v1/auth/reset-password` | public (link from email) |
| `POST` | `/api/v1/auth/logout` | signed in |
| `GET` | `/api/v1/auth/me` | signed in |
| `GET` | `/api/v1/downloads/` | verified member |
| `GET` | `/api/v1/downloads/{id}` | verified member |
| `POST` | `/api/v1/downloads/` | admin |
| `PATCH` | `/api/v1/downloads/{id}` | admin |
| `DELETE` | `/api/v1/downloads/{id}` | admin |

## Project layout

```
gzone/
├── backend/            # FastAPI application (+ Dockerfile)
├── frontend/           # Next.js application
├── docker-compose.yml  # PostgreSQL, Redis, Mailpit
└── DEPLOYMENT.md       # deploying all five services on free tiers
```

The API can also run containerised, which is how a host builds it:

```bash
docker compose --profile full up -d --build
```

## Progress

- [x] Repository and backend skeleton
- [x] PostgreSQL via Docker Compose, async SQLModel, CRUD
- [x] Alembic migrations
- [x] Registration and password hashing, service layer
- [x] JWT login, authenticated and admin dependencies
- [x] Members-only downloads with role-based access
- [x] Redis token blacklist and logout
- [x] Email verification
- [x] Password reset
- [x] CORS, uniform error handling, request logging
- [x] pytest suite (56 tests, 93% coverage)
- [x] Frontend shell and home page
- [x] About page and locked downloads page
- [x] Frontend auth: sign up, confirm, sign in, sign out
- [x] Frontend password reset
- [x] Profile page
- [x] Admin area for managing download links
- [ ] Celery for background email
- [x] Dockerfile for the API
- [ ] Deployment to free-tier hosting — see [DEPLOYMENT.md](DEPLOYMENT.md)
