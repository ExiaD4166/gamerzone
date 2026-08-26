from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

# expire_on_commit=False keeps attributes readable after a commit instead of forcing
# a fresh round-trip the next time one is touched.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Hand each request its own session, closed afterwards even if the request fails."""
    async with async_session_maker() as session:
        yield session
