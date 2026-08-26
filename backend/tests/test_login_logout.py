"""Signing in, holding a session, and giving it up again."""

import base64
import json

from httpx import AsyncClient

from app.models.user import User
from tests.conftest import TEST_PASSWORD, login_headers


def _decode_jwt_payload(token: str) -> dict:
    """Read a JWT's claims without the secret key - which anyone can do, hence the rule
    that nothing confidential goes in there."""
    payload_b64 = token.split(".")[1]
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))


async def test_login_returns_a_bearer_token(client: AsyncClient, member: User) -> None:
    response = await client.post(
        "/api/v1/auth/login", data={"username": member.email, "password": TEST_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_token_identifies_the_user_and_expires(client: AsyncClient, member: User) -> None:
    response = await client.post(
        "/api/v1/auth/login", data={"username": member.email, "password": TEST_PASSWORD}
    )

    claims = _decode_jwt_payload(response.json()["access_token"])
    assert claims["sub"] == str(member.id)
    assert claims["exp"] > claims["iat"]  # expires in the future, not the past
    assert claims["jti"]  # unique per token, used by the blacklist


async def test_each_login_issues_a_distinct_token(client: AsyncClient, member: User) -> None:
    """Two sessions of the same account must be separately revocable."""
    first = await login_headers(client, member.email)
    second = await login_headers(client, member.email)

    jti_one = _decode_jwt_payload(first["Authorization"].split()[1])["jti"]
    jti_two = _decode_jwt_payload(second["Authorization"].split()[1])["jti"]
    assert jti_one != jti_two


async def test_wrong_password_is_refused(client: AsyncClient, member: User) -> None:
    response = await client.post(
        "/api/v1/auth/login", data={"username": member.email, "password": "not_the_password"}
    )

    assert response.status_code == 401


async def test_unknown_email_and_wrong_password_look_identical(
    client: AsyncClient, member: User
) -> None:
    """Different replies would let an attacker map which addresses are registered."""
    wrong_password = await client.post(
        "/api/v1/auth/login", data={"username": member.email, "password": "not_the_password"}
    )
    unknown_email = await client.post(
        "/api/v1/auth/login", data={"username": "ghost@example.com", "password": TEST_PASSWORD}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json()["detail"] == unknown_email.json()["detail"]


async def test_me_returns_the_signed_in_user(
    client: AsyncClient, member: User, member_headers: dict
) -> None:
    response = await client.get("/api/v1/auth/me", headers=member_headers)

    assert response.status_code == 200
    assert response.json()["email"] == member.email
    assert "hashed_password" not in response.json()


async def test_me_requires_a_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


async def test_garbage_token_is_refused(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"}
    )

    assert response.status_code == 401


async def test_tampered_token_is_refused(client: AsyncClient, member_headers: dict) -> None:
    """Rewriting the payload to claim another user breaks the signature."""
    token = member_headers["Authorization"].split()[1]
    header_b64, payload_b64, signature = token.split(".")

    claims = _decode_jwt_payload(token)
    claims["sub"] = "9999"
    forged_payload = (
        base64.urlsafe_b64encode(json.dumps(claims, separators=(",", ":")).encode())
        .rstrip(b"=")
        .decode()
    )
    forged = f"{header_b64}.{forged_payload}.{signature}"

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


async def test_logout_revokes_the_token(
    client: AsyncClient, member: User, member_headers: dict
) -> None:
    assert (await client.get("/api/v1/auth/me", headers=member_headers)).status_code == 200

    logout = await client.post("/api/v1/auth/logout", headers=member_headers)
    assert logout.status_code == 204

    after = await client.get("/api/v1/auth/me", headers=member_headers)
    assert after.status_code == 401


async def test_logout_only_affects_that_session(client: AsyncClient, member: User) -> None:
    """Signing out on one device must leave the user's other devices signed in."""
    laptop = await login_headers(client, member.email)
    phone = await login_headers(client, member.email)

    await client.post("/api/v1/auth/logout", headers=laptop)

    assert (await client.get("/api/v1/auth/me", headers=laptop)).status_code == 401
    assert (await client.get("/api/v1/auth/me", headers=phone)).status_code == 200


async def test_deactivated_account_is_refused(
    client: AsyncClient, session, member: User, member_headers: dict
) -> None:
    """A token stays signed and unexpired, but the account behind it can change."""
    member.is_active = False
    session.add(member)
    await session.commit()

    response = await client.get("/api/v1/auth/me", headers=member_headers)
    assert response.status_code == 403
