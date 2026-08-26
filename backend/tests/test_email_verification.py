"""Confirming an email address, and what a verification link will and won't do."""

import re
import time
from unittest.mock import patch

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.tokens import (
    generate_email_verification_token,
    generate_password_reset_token,
)
from app.models.user import User

SIGNUP = {"email": "rookie@example.com", "username": "rookie", "password": "a_strong_password"}


def extract_token(email_body: str) -> str:
    """Pull the token out of a link in the message, the way a user clicks it."""
    match = re.search(r"token=([A-Za-z0-9_.\-]+)", email_body)
    assert match, f"no token found in email:\n{email_body}"
    return match.group(1)


async def test_verification_link_confirms_the_account(
    client: AsyncClient, session: AsyncSession, sent_emails: list
) -> None:
    await client.post("/api/v1/auth/signup", json=SIGNUP)
    token = extract_token(sent_emails[0]["plain_body"])

    response = await client.get("/api/v1/auth/verify", params={"token": token})

    assert response.status_code == 200
    user = await session.get(User, 1)
    assert user is not None and user.is_verified is True


async def test_clicking_the_link_twice_is_harmless(
    client: AsyncClient, sent_emails: list
) -> None:
    await client.post("/api/v1/auth/signup", json=SIGNUP)
    token = extract_token(sent_emails[0]["plain_body"])

    first = await client.get("/api/v1/auth/verify", params={"token": token})
    second = await client.get("/api/v1/auth/verify", params={"token": token})

    assert first.status_code == 200
    assert second.status_code == 200


async def test_tampered_token_is_rejected(client: AsyncClient, sent_emails: list) -> None:
    await client.post("/api/v1/auth/signup", json=SIGNUP)
    token = extract_token(sent_emails[0]["plain_body"])

    response = await client.get("/api/v1/auth/verify", params={"token": token[:-1] + "X"})

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_token"


async def test_expired_token_is_rejected(client: AsyncClient, sent_emails: list) -> None:
    """Minted 25 hours ago against a 24-hour limit. Faking the clock at generation
    time is the only practical way to test expiry without actually waiting."""
    await client.post("/api/v1/auth/signup", json=SIGNUP)

    with patch("time.time", return_value=time.time() - 25 * 3600):
        stale_token = generate_email_verification_token(SIGNUP["email"])

    response = await client.get("/api/v1/auth/verify", params={"token": stale_token})
    assert response.status_code == 400


async def test_a_password_reset_token_cannot_verify_an_email(
    client: AsyncClient, sent_emails: list
) -> None:
    """The salt scopes a token to one purpose - this is what stops one flow's link
    being replayed against another."""
    await client.post("/api/v1/auth/signup", json=SIGNUP)
    wrong_purpose = generate_password_reset_token(SIGNUP["email"], "irrelevant-hash")

    response = await client.get("/api/v1/auth/verify", params={"token": wrong_purpose})
    assert response.status_code == 400


async def test_token_for_a_deleted_account_is_rejected(client: AsyncClient) -> None:
    token = generate_email_verification_token("never-existed@example.com")

    response = await client.get("/api/v1/auth/verify", params={"token": token})
    assert response.status_code == 400


async def test_resend_sends_a_new_link_to_an_unverified_account(
    client: AsyncClient, unverified_member: User, sent_emails: list
) -> None:
    response = await client.post(
        "/api/v1/auth/resend-verification", params={"email": unverified_member.email}
    )

    assert response.status_code == 202
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == unverified_member.email


async def test_resend_says_nothing_about_who_exists(
    client: AsyncClient, member: User, sent_emails: list
) -> None:
    """Already-verified and entirely unknown addresses must be indistinguishable, or
    this endpoint becomes a way to enumerate accounts."""
    already_verified = await client.post(
        "/api/v1/auth/resend-verification", params={"email": member.email}
    )
    unknown = await client.post(
        "/api/v1/auth/resend-verification", params={"email": "ghost@example.com"}
    )

    assert already_verified.status_code == unknown.status_code == 202
    assert already_verified.json() == unknown.json()
    assert sent_emails == []  # neither case actually sends anything
