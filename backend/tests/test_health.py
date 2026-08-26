"""Smoke tests: if these fail, nothing else is worth looking at."""

from httpx import AsyncClient


async def test_root_responds(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "GamerZone" in response.json()["message"]


async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_every_response_carries_a_request_id(client: AsyncClient) -> None:
    """The middleware should tag responses so a report can be traced to a log line."""
    response = await client.get("/api/v1/health")
    assert response.headers.get("X-Request-ID")
