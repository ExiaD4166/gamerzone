from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Runs once when the server starts (before `yield`) and once when it shuts down
    (after `yield`). We use the startup half to make sure our tables exist."""
    await init_db()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "GamerZone API is running. Visit /docs for the interactive API docs."}
