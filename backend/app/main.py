from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Runs once on startup (before `yield`) and once on shutdown (after `yield`).

    The schema is NOT created here - that is Alembic's job (`alembic upgrade head`),
    so that schema changes are explicit, reviewable and reversible rather than a
    silent side effect of booting the server. Shutdown closes the connection pool
    cleanly instead of dropping live connections.
    """
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "GamerZone API is running. Visit /docs for the interactive API docs."}
