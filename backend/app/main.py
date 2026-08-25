import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.middleware import request_context_middleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.redis import redis_client
from app.db.session import engine

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Runs once on startup (before `yield`) and once on shutdown (after `yield`).

    The schema is NOT created here - that is Alembic's job (`alembic upgrade head`),
    so that schema changes are explicit, reviewable and reversible rather than a
    silent side effect of booting the server. Shutdown closes the connection pool
    cleanly instead of dropping live connections.
    """
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Allowed CORS origins: %s", ", ".join(settings.cors_origins_list))
    yield
    logger.info("Shutting down, releasing connections")
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

# Middleware runs in reverse registration order on the way in, so the request context
# (and its id) is established before CORS or anything else can short-circuit a request.
app.middleware("http")(request_context_middleware)

app.add_middleware(
    CORSMiddleware,
    # An explicit list, not "*". A wildcard is rejected by browsers when credentials
    # are allowed, and would mean any site could call this API with a user's token.
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Without this the browser hides the header from frontend JavaScript entirely.
    expose_headers=["X-Request-ID"],
)

register_error_handlers(app)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "GamerZone API is running. Visit /docs for the interactive API docs."}
