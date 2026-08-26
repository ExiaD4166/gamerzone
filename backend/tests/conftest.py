"""Shared test fixtures.

pytest loads this file automatically, so every test module can request the fixtures
below by name without importing anything.

Two rules shape the whole setup:
  * tests run against real PostgreSQL and real Redis, never SQLite or a fake, because
    the app relies on Postgres-specific behaviour (timestamptz, SERIAL, UNIQUE
    constraints) - a suite that passes on a different engine proves very little;
  * tests never touch development data. They use a separate database and a separate
    Redis numbered database, and every table is emptied between tests so no test can
    depend on, or be confused by, another one's leftovers.
"""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.db.redis as redis_module
import app.models  # noqa: F401  - imported so SQLModel.metadata knows every table
import app.services.mail_service as mail_service
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import get_session
from app.main import app
from app.models.user import User

# Same server and credentials as development, different database name. Overridable so
# a CI pipeline can point somewhere else.
_DB_ROOT, _DEV_DB_NAME = settings.database_url.rsplit("/", 1)
TEST_DB_NAME = "gamerzone_test"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", f"{_DB_ROOT}/{TEST_DB_NAME}")

# Redis keeps 16 numbered databases on one server; the app uses 0, so tests take the
# last one and can flush it freely.
TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", f"{settings.redis_url.rsplit('/', 1)[0]}/15")


async def _ensure_test_database_exists() -> None:
    """CREATE DATABASE gamerzone_test, if it isn't there yet.

    Connects to the always-present "postgres" maintenance database to do it, and needs
    AUTOCOMMIT because Postgres refuses to run CREATE DATABASE inside a transaction.
    """
    engine = create_async_engine(f"{_DB_ROOT}/postgres", isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME}
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine() -> AsyncGenerator:
    """One engine for the whole run, with the schema built once up front.

    The schema comes from SQLModel.metadata rather than from Alembic: it is the same
    definition the migrations are generated from, and building it directly keeps the
    suite fast enough to run constantly. (Applying the migrations instead is a
    worthwhile separate check to add in CI.)
    """
    await _ensure_test_database_exists()

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """A database session for one test, followed by a clean slate.

    TRUNCATE ... RESTART IDENTITY empties every table and resets the id counters, so
    each test can rely on the first row it creates having id 1. CASCADE handles tables
    referenced by foreign keys once relationships exist.
    """
    maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as db_session:
        yield db_session

    table_names = ", ".join(f'"{table}"' for table in SQLModel.metadata.tables)
    async with test_engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture(loop_scope="session")
async def redis_test_client(monkeypatch) -> AsyncGenerator[Redis, None]:
    """Point the app's Redis client at the test database and empty it afterwards.

    app.db.redis exposes one module-level client, so replacing that attribute makes
    every caller - including get_current_user's blacklist check - use this one.
    """
    client = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    monkeypatch.setattr(redis_module, "redis_client", client)

    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def sent_emails(monkeypatch) -> list[dict[str, str]]:
    """Capture outgoing mail instead of sending it.

    Replacing send_email keeps SMTP out of the tests entirely, while everything above
    it - token generation, link building, the background task - still runs for real.
    Tests read the captured body to get the verification or reset link, exactly as a
    user would read it in their inbox.
    """
    captured: list[dict[str, str]] = []

    async def fake_send_email(to: str, subject: str, plain_body: str, html_body: str) -> None:
        captured.append(
            {"to": to, "subject": subject, "plain_body": plain_body, "html_body": html_body}
        )

    monkeypatch.setattr(mail_service, "send_email", fake_send_email)
    return captured


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    session: AsyncSession, redis_test_client: Redis, sent_emails: list
) -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client wired straight into the app.

    ASGITransport calls the application in-process - no uvicorn, no sockets, no port -
    so requests are fast and nothing leaks between test runs.

    dependency_overrides swaps get_session for one that hands back the test session, so
    the endpoints write to the test database. It's cleared afterwards to avoid leaking
    into other tests.
    """

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

    app.dependency_overrides.clear()


# --- Ready-made accounts -----------------------------------------------------------
# Built directly through the model rather than by calling the signup endpoint: it's
# faster, and it can set flags like is_verified and is_superuser that the API
# deliberately refuses to expose.

TEST_PASSWORD = "test_password_123"


async def _create_user(
    session: AsyncSession,
    *,
    email: str,
    username: str,
    is_verified: bool = True,
    is_superuser: bool = False,
    is_active: bool = True,
) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(TEST_PASSWORD),
        is_verified=is_verified,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login_headers(client: AsyncClient, email: str, password: str = TEST_PASSWORD) -> dict:
    """Sign in and return the Authorization header for the resulting token."""
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200, f"login failed: {response.text}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest_asyncio.fixture(loop_scope="session")
async def member(session: AsyncSession) -> User:
    """An ordinary member who has confirmed their email."""
    return await _create_user(session, email="member@example.com", username="member")


@pytest_asyncio.fixture(loop_scope="session")
async def unverified_member(session: AsyncSession) -> User:
    """Signed up but has not clicked the verification link."""
    return await _create_user(
        session, email="unverified@example.com", username="unverified", is_verified=False
    )


@pytest_asyncio.fixture(loop_scope="session")
async def admin(session: AsyncSession) -> User:
    return await _create_user(
        session, email="admin@example.com", username="admin", is_superuser=True
    )


@pytest_asyncio.fixture(loop_scope="session")
async def member_headers(client: AsyncClient, member: User) -> dict:
    return await login_headers(client, member.email)


@pytest_asyncio.fixture(loop_scope="session")
async def admin_headers(client: AsyncClient, admin: User) -> dict:
    return await login_headers(client, admin.email)
