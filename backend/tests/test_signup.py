"""Registration: what gets accepted, what gets rejected, and what comes back."""

from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import verify_password
from app.models.user import User

VALID_SIGNUP = {
    "email": "newplayer@example.com",
    "username": "newplayer",
    "password": "a_strong_password",
}


async def test_signup_creates_account(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_SIGNUP["email"]
    assert body["username"] == VALID_SIGNUP["username"]
    assert body["id"] == 1


async def test_signup_never_returns_the_password(client: AsyncClient) -> None:
    """The response model is the guard that makes leaking a hash impossible."""
    response = await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)

    body = response.json()
    assert "password" not in body
    assert "hashed_password" not in body


async def test_signup_stores_a_hash_not_the_password(
    client: AsyncClient, session: AsyncSession
) -> None:
    await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)

    user = (await session.exec(select(User).where(User.email == VALID_SIGNUP["email"]))).one()
    assert user.hashed_password != VALID_SIGNUP["password"]
    assert user.hashed_password.startswith("$argon2")
    # ...and the stored hash really does correspond to the password given.
    assert verify_password(VALID_SIGNUP["password"], user.hashed_password)


async def test_new_accounts_start_unverified_and_unprivileged(
    client: AsyncClient, session: AsyncSession
) -> None:
    await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)

    user = (await session.exec(select(User).where(User.email == VALID_SIGNUP["email"]))).one()
    assert user.is_verified is False
    assert user.is_superuser is False
    assert user.is_active is True


async def test_signup_cannot_grant_itself_admin(
    client: AsyncClient, session: AsyncSession
) -> None:
    """is_superuser isn't part of UserCreate, so sending it must have no effect."""
    await client.post("/api/v1/auth/signup", json={**VALID_SIGNUP, "is_superuser": True})

    user = (await session.exec(select(User).where(User.email == VALID_SIGNUP["email"]))).one()
    assert user.is_superuser is False


async def test_duplicate_email_is_rejected(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    response = await client.post(
        "/api/v1/auth/signup", json={**VALID_SIGNUP, "username": "someone_else"}
    )

    assert response.status_code == 409
    assert response.json()["code"] == "email_already_exists"


async def test_duplicate_username_is_rejected(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    response = await client.post(
        "/api/v1/auth/signup", json={**VALID_SIGNUP, "email": "other@example.com"}
    )

    assert response.status_code == 409
    assert response.json()["code"] == "username_already_taken"


async def test_signup_sends_a_verification_email(
    client: AsyncClient, sent_emails: list
) -> None:
    await client.post("/api/v1/auth/signup", json=VALID_SIGNUP)

    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == VALID_SIGNUP["email"]
    assert "verify" in sent_emails[0]["subject"].lower()


async def test_invalid_email_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/signup", json={**VALID_SIGNUP, "email": "not-an-email"}
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_short_password_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/signup", json={**VALID_SIGNUP, "password": "short"})

    assert response.status_code == 422


async def test_short_username_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/signup", json={**VALID_SIGNUP, "username": "ab"})

    assert response.status_code == 422
