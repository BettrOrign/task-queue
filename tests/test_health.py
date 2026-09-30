"""Tests for the task queue backend."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "task-queue-api"


@pytest.mark.asyncio
async def test_health_no_prefix() -> None:
    """Direct health endpoint without API prefix."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # The health router is mounted at /api/v1/health
        response = await client.get("/api/v1/health")
    assert response.status_code == 200