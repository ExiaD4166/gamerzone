# GamerZone

A gaming community website: homepage, about page, member profiles, and a members-only download page for
game/mod links. Built as a learning project to practice an industry-style full-stack workflow.

**Stack**
- Backend: FastAPI, SQLModel, PostgreSQL (async), Redis, Celery — see [`backend/README.md`](backend/README.md)
- Frontend: Next.js + TypeScript — added in a later phase
- Auth: OAuth2 password flow with JWT, email verification
- Infra: Docker Compose locally, deployed on free-tier hosting

**Status:** early development — backend foundations only. This README will grow as each phase lands.

## Project layout

```
gzone/
├── backend/    # FastAPI application
└── frontend/   # Next.js application (not created yet)
```

## Development log

- Phase 0 — repository and backend skeleton (FastAPI app, versioned API router, health check).
