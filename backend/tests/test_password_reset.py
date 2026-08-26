"""Password reset: the happy path, and the three things that must never work."""

import time
from unittest.mock import patch

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.tokens import (
    generate_email_verification_token,
    generate_password_reset_token,
)
from app.models.user import User
from tests.conftest import TEST_PASSWORD, login_headers
from tests.test_email_verification import extract_token

NEW_PASSWORD = "a_completely_new_password"


async def _request_reset(client: AsyncClient, email: str, sent_emails: list) -> str:
    """Run the forgot-password step and return the token from the resulting email."""
    response = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert response.status_code == 202
    return extract_token(sent_emails[-1]["plain_body"])


async def test_reset_changes_the_password(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    token = await _request_reset(client, member.email, sent_emails)

    response = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 200
    # the new password works...
    assert (
        await client.post(
            "/api/v1/auth/login", data={"username": member.email, "password": NEW_PASSWORD}
        )
    ).status_code == 200
    # ...and the old one no longer does
    assert (
        await client.post(
            "/api/v1/auth/login", data={"username": member.email, "password": TEST_PASSWORD}
        )
    ).status_code == 401


async def test_reset_email_goes_to_the_right_address(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    await client.post("/api/v1/auth/forgot-password", json={"email": member.email})

    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == member.email
    assert "reset" in sent_emails[0]["subject"].lower()


async def test_the_reset_link_works_only_once(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    """Completing a reset changes the password hash, which no longer matches the
    fingerprint baked into the token - so the link dies as a side effect of being used.
    Without this, anyone who later reached the inbox could take the account over."""
    token = await _request_reset(client, member.email, sent_emails)

    first = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )
    second = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "attacker_chosen_password"},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["code"] == "invalid_token"


async def test_reset_signs_out_every_existing_session(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    """The point of resetting a compromised account is that the intruder loses access
    immediately, not in thirty minutes when their token happens to expire."""
    existing_session = await login_headers(client, member.email)
    assert (await client.get("/api/v1/auth/me", headers=existing_session)).status_code == 200

    token = await _request_reset(client, member.email, sent_emails)
    await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )

    assert (await client.get("/api/v1/auth/me", headers=existing_session)).status_code == 401


async def test_reset_records_when_the_password_changed(
    client: AsyncClient, session: AsyncSession, member: User, sent_emails: list
) -> None:
    assert member.password_changed_at is None

    token = await _request_reset(client, member.email, sent_emails)
    await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )

    await session.refresh(member)
    assert member.password_changed_at is not None


async def test_expired_reset_token_is_rejected(client: AsyncClient, member: User) -> None:
    """Two hours old against a sixty-minute limit."""
    with patch("time.time", return_value=time.time() - 7200):
        stale = generate_password_reset_token(member.email, member.hashed_password)

    response = await client.post(
        "/api/v1/auth/reset-password", json={"token": stale, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400


async def test_a_verification_token_cannot_reset_a_password(
    client: AsyncClient, member: User
) -> None:
    wrong_purpose = generate_email_verification_token(member.email)

    response = await client.post(
        "/api/v1/auth/reset-password", json={"token": wrong_purpose, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400


async def test_tampered_reset_token_is_rejected(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    token = await _request_reset(client, member.email, sent_emails)

    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token[:-1] + "X", "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 400


async def test_forgot_password_reveals_nothing_about_unknown_addresses(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    known = await client.post("/api/v1/auth/forgot-password", json={"email": member.email})
    unknown = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "ghost@example.com"}
    )

    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()
    # ...but only the real account was actually emailed
    assert [mail["to"] for mail in sent_emails] == [member.email]


async def test_reset_cannot_set_a_weaker_password_than_signup_allows(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    token = await _request_reset(client, member.email, sent_emails)

    response = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "short"}
    )
    assert response.status_code == 422
