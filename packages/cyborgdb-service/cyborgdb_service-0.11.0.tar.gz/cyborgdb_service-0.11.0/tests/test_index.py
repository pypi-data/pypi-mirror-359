import pytest
import httpx
from httpx import ASGITransport
import asyncio

from cyborgdb_service.app import app
from cyborgdb_service.core.config import settings
from cyborgdb_service.api.schemas.index import (
    CreateIndexRequest, IndexOperationRequest, TrainRequest
)

# Constants
API_PREFIX = settings.API_PREFIX
HEADERS = {"X-API-Key": settings.SERVICE_API_KEY}
INDEX_NAME = "test-index"
INDEX_KEY ="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
# Example index config (IVFFLAT)
INDEX_CONFIG = {
    "type": "ivfflat",
    "n_lists": 16,
    "metric": "euclidean",
    "dimension": 128,
    "pq_dim": 16,
    "pq_bits": 8
}

@pytest.mark.asyncio
async def test_create_index():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = CreateIndexRequest(
            index_name=INDEX_NAME,
            index_key=INDEX_KEY,
            index_config=INDEX_CONFIG
        ).dict()
        response = await ac.post("/indexes/create", json=payload, headers=HEADERS)
        print("Create Index Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_list_indexes():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.get("/indexes/list", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        print("List Indexes Response:", data)
        assert "indexes" in data
        assert isinstance(data["indexes"], list)
        assert INDEX_NAME in data["indexes"]

@pytest.mark.asyncio
async def test_describe_index():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = IndexOperationRequest(index_name=INDEX_NAME, index_key=INDEX_KEY).dict()
        response = await ac.post("/indexes/describe", json=payload, headers=HEADERS)
        print("Create test_describe_index Response:", response.status_code, response.text)
        assert response.status_code == 200
        data = response.json()
        # Top-level fields
        assert data["index_name"] == INDEX_NAME
        assert data["index_type"] == "ivfflat"
        assert data["is_trained"] is False
        assert "index_config" in data

        # Nested config checks
        config = data["index_config"]
        assert config["dimension"] == INDEX_CONFIG["dimension"]
        assert config["metric"] == INDEX_CONFIG["metric"]
        assert config["index_type"] == INDEX_CONFIG["type"]
        assert config["n_lists"] == INDEX_CONFIG["n_lists"]

@pytest.mark.asyncio
async def test_delete_index():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = IndexOperationRequest(index_name=INDEX_NAME, index_key=INDEX_KEY).dict()
        response = await ac.post("/indexes/delete", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_create_bad_index():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = CreateIndexRequest(
            index_name=INDEX_NAME,
            index_key="1234567890",
            index_config=INDEX_CONFIG
        ).dict()
        response = await ac.post("/indexes/create", json=payload, headers=HEADERS)
        print("Create Index Response bad 1:", response.status_code, response.text)
        assert response.status_code == 400

        # Invalid config: missing 'metric'
        bad_config = dict(INDEX_CONFIG)
        bad_config["n_lists"] = 0

        payload = {
            "index_name": "bad_index",
            "index_key": INDEX_KEY,
            "index_config": bad_config
        }
        response = await ac.post("/indexes/create", json=payload, headers=HEADERS)
        print("Create Index Response bad 2:", response.status_code, response.text)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_delete_index_error():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = IndexOperationRequest(index_name="not real", index_key=INDEX_KEY).dict()
        response = await ac.post("/indexes/delete", json=payload, headers=HEADERS)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_api_key():
    headers = {"X-API-Key": "wfiwehhwegihweui"}
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.get("/indexes/list", headers=headers)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_method_not_allowed():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/indexes/list", headers=HEADERS)
        assert response.status_code == 405

@pytest.mark.asyncio
async def test_malformed_json():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/indexes/create", content="{bad json", headers={**HEADERS, "Content-Type": "application/json"})
        assert response.status_code == 400 or response.status_code == 422

@pytest.mark.asyncio
async def test_create_index_missing_fields():
    bad_payload = {"index_name": "test"}  # Missing index_key, index_config
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/indexes/create", json=bad_payload, headers=HEADERS)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_invalid_index_config_type():
    payload = {
        "index_name": INDEX_NAME,
        "index_key": INDEX_KEY,
        "index_config": "this_should_be_a_dict"
    }
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/indexes/create", json=payload, headers=HEADERS)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_response_format_consistency():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.get("/indexes/list", headers=HEADERS)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "indexes" in response.json()

@pytest.mark.asyncio
async def test_concurrent_index_list():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        responses = await asyncio.gather(
            ac.get("/indexes/list", headers=HEADERS),
            ac.get("/indexes/list", headers=HEADERS),
            ac.get("/indexes/list", headers=HEADERS)
        )
        for resp in responses:
            assert resp.status_code == 200

@pytest.mark.asyncio
async def test_missing_content_type_header():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        # application/json is implied by using json=, so we force raw content
        response = await ac.post("/indexes/create", data="{}", headers=HEADERS)
        assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_boundary_n_lists_zero():
    bad_config = {
        "type": "ivfflat",
        "n_lists": 0,  # invalid
        "metric": "euclidean",
        "dimension": 128
    }
    payload = {
        "index_name": "bad-index",
        "index_key": INDEX_KEY,
        "index_config": bad_config
    }
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/indexes/create", json=payload, headers=HEADERS)
        assert response.status_code in (400, 422)

@pytest.mark.asyncio
@pytest.mark.parametrize("method,endpoint", [
    ("GET", "/indexes/list"),
    ("POST", "/indexes/create"),
    ("POST", "/indexes/describe"),
    ("POST", "/indexes/train"),
    ("POST", "/indexes/delete"),
])
async def test_missing_api_key_returns_401(method, endpoint):
    transport = ASGITransport(app=app)
    url = f"http://test{API_PREFIX}{endpoint}"
    
    # Dummy payloads where required
    payload = {
        "/indexes/create": {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "index_config": {
                "type": "ivfflat",
                "n_lists": 16,
                "metric": "euclidean",
                "dimension": 128
            }
        },
        "/indexes/describe": {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY
        },
        "/indexes/delete": {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY
        },
        "/indexes/train": {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "batch_size": 512,
            "max_iters": 10,
            "tolerance": 1e-4,
            "max_memory": 256
        }
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        if method == "GET":
            response = await ac.get(url)  # no headers
        else:
            response = await ac.post(url, json=payload.get(endpoint, {}))  # no headers

        assert response.status_code == 401
        assert "detail" in response.json()