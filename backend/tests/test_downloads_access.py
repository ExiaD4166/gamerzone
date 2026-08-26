"""The members-only download page: who can see the links, and who can change them.

The rule being enforced:
    anonymous        -> 401, cannot see anything
    unverified       -> 403, signing up isn't proof you own the address
    verified member  -> may read
    admin            -> may also create, edit and delete
"""

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.download_item import DownloadItem
from app.models.user import User
from tests.conftest import login_headers

ITEM = {
    "title": "GamerZone Launcher",
    "category": "game",
    "url": "https://drive.google.com/example",
    "description": "Main installer",
}


async def _seed_item(session: AsyncSession) -> DownloadItem:
    item = DownloadItem(**ITEM)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


# --- reading ----------------------------------------------------------------------


async def test_anonymous_cannot_see_the_links(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_item(session)

    response = await client.get("/api/v1/downloads/")

    assert response.status_code == 401
    assert "drive.google.com" not in response.text


async def test_unverified_member_cannot_see_the_links(
    client: AsyncClient, session: AsyncSession, unverified_member: User
) -> None:
    await _seed_item(session)
    headers = await login_headers(client, unverified_member.email)

    response = await client.get("/api/v1/downloads/", headers=headers)

    assert response.status_code == 403
    assert "drive.google.com" not in response.text


async def test_verified_member_can_see_the_links(
    client: AsyncClient, session: AsyncSession, member_headers: dict
) -> None:
    await _seed_item(session)

    response = await client.get("/api/v1/downloads/", headers=member_headers)

    assert response.status_code == 200
    assert response.json()[0]["url"] == ITEM["url"]


async def test_member_can_fetch_one_item(
    client: AsyncClient, session: AsyncSession, member_headers: dict
) -> None:
    item = await _seed_item(session)

    response = await client.get(f"/api/v1/downloads/{item.id}", headers=member_headers)

    assert response.status_code == 200
    assert response.json()["title"] == ITEM["title"]


async def test_missing_item_returns_404(client: AsyncClient, member_headers: dict) -> None:
    response = await client.get("/api/v1/downloads/999", headers=member_headers)

    assert response.status_code == 404


# --- writing ----------------------------------------------------------------------


async def test_member_cannot_add_an_item(client: AsyncClient, member_headers: dict) -> None:
    response = await client.post("/api/v1/downloads/", json=ITEM, headers=member_headers)

    assert response.status_code == 403


async def test_member_cannot_delete_an_item(
    client: AsyncClient, session: AsyncSession, member_headers: dict
) -> None:
    item = await _seed_item(session)

    response = await client.delete(f"/api/v1/downloads/{item.id}", headers=member_headers)

    assert response.status_code == 403


async def test_admin_can_add_an_item(client: AsyncClient, admin_headers: dict) -> None:
    response = await client.post("/api/v1/downloads/", json=ITEM, headers=admin_headers)

    assert response.status_code == 201
    assert response.json()["title"] == ITEM["title"]


async def test_admin_can_edit_one_field_without_disturbing_the_rest(
    client: AsyncClient, session: AsyncSession, admin_headers: dict
) -> None:
    """PATCH uses exclude_unset, so fields the client didn't send stay as they were."""
    item = await _seed_item(session)

    response = await client.patch(
        f"/api/v1/downloads/{item.id}",
        json={"description": "Updated description"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Updated description"
    assert body["title"] == ITEM["title"]
    assert body["url"] == ITEM["url"]


async def test_admin_can_delete_an_item(
    client: AsyncClient, session: AsyncSession, admin_headers: dict, member_headers: dict
) -> None:
    item = await _seed_item(session)

    response = await client.delete(f"/api/v1/downloads/{item.id}", headers=admin_headers)

    assert response.status_code == 204
    remaining = await client.get("/api/v1/downloads/", headers=member_headers)
    assert remaining.json() == []


async def test_unverified_admin_cannot_write_either(
    client: AsyncClient, session: AsyncSession
) -> None:
    """Admin sits on top of verified, not beside it - the levels are strictly nested."""
    from tests.conftest import _create_user

    unverified_admin = await _create_user(
        session,
        email="unverified-admin@example.com",
        username="unverifiedadmin",
        is_verified=False,
        is_superuser=True,
    )
    headers = await login_headers(client, unverified_admin.email)

    response = await client.post("/api/v1/downloads/", json=ITEM, headers=headers)
    assert response.status_code == 403


async def test_a_revoked_token_loses_access_to_the_links(
    client: AsyncClient, session: AsyncSession, member: User, member_headers: dict
) -> None:
    await _seed_item(session)
    assert (await client.get("/api/v1/downloads/", headers=member_headers)).status_code == 200

    await client.post("/api/v1/auth/logout", headers=member_headers)

    assert (await client.get("/api/v1/downloads/", headers=member_headers)).status_code == 401
