# tests/test_health.py
import pytest
import httpx
from httpx import ASGITransport

from cyborgdb_service.app import app

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "api_version" in data
    assert "version" in data
