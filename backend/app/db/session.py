from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# The engine manages a pool of connections to Postgres. Creating it does NOT open a
# connection yet - it's just the factory everything else pulls connections from.
# echo=True (only when DEBUG=true) prints every SQL statement SQLModel generates,
# which is extremely useful while learning what an ORM is actually doing.
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Factory for creating new AsyncSession objects bound to that engine.
# expire_on_commit=False keeps attributes on an object readable after commit,
# instead of forcing a fresh DB round-trip the next time you touch it.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: hands each request its own database session, and guarantees
    it gets closed afterwards - even if the request raises an exception - because
    `async with` is a context manager (this is the same `with` concept from your course,
    just the async version)."""
    async with async_session_maker() as session:
        yield session
