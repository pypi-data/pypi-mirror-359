import pytest
import httpx
from httpx import ASGITransport
import asyncio

from cyborgdb_service.app import app
from cyborgdb_service.core.config import settings
from cyborgdb_service.api.schemas.vectors import VectorItem
from cyborgdb_service.api.schemas.index import (CreateIndexRequest,IndexOperationRequest,TrainRequest)
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
async def test_create_and_upsert_index():
    transport = ASGITransport(app=app)

    # Create a list of 100 text entries with varied content
    dict_data = [
        {"id": str(i), "contents": f"Sentence {i} about foxes and dogs"}
        if i % 5 == 0 else
        {"id": str(i), "contents": f"Random topic {i} involving AI and technology"}
        if i % 3 == 0 else
        {"id": str(i), "contents": f"A philosophical discussion {i} on ethics and society"}
        if i % 7 == 0 else
        {"id": str(i), "contents": f"A discussion {i} on history and civilization"}
        if i % 9 == 0 else
        {"id": str(i), "contents": f"Simple test phrase {i}"}
        for i in range(100)
    ]

    # Add optional metadata to each item
    for item in dict_data:
        item["metadata"] = {"source": "test", "length": len(item["contents"])}

    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        # Step 1: Create the index
        create_payload = CreateIndexRequest(
            index_name=INDEX_NAME,
            index_key=INDEX_KEY,
            index_config=INDEX_CONFIG,
            embedding_model="all-MiniLM-L6-v2"
        ).dict()
        create_response = await ac.post("/indexes/create", json=create_payload, headers=HEADERS)
        print("Create Index Response:", create_response.status_code, create_response.text)
        assert create_response.status_code == 200
        assert create_response.json()["status"] == "success"

        # Step 2: Upsert vector
        upsert_payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "items": dict_data

        }
        upsert_response = await ac.post("/vectors/upsert", json=upsert_payload, headers=HEADERS)
        print("Upsert Response:", upsert_response.status_code, upsert_response.text)
        assert upsert_response.status_code == 200
        assert "Upserted" in upsert_response.json().get("message", "")

        #step 3: train
        payload = TrainRequest(
            index_name=INDEX_NAME,
            index_key=INDEX_KEY,
            batch_size=256,
            max_iters=50,
            tolerance=1e-6,
            max_memory=0
        ).dict()
        response = await ac.post("/indexes/train", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_query_vector():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "query_contents": "documents",
            "top_k": 1
        }
        response = await ac.post("/vectors/query", json=payload, headers=HEADERS)
        print("Query Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert "results" in response.json()

@pytest.mark.asyncio
async def test_get_vector():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "ids": ["0"]
        }
        response = await ac.post("/vectors/get", json=payload, headers=HEADERS)
        print("Get Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert response.json()["results"][0]["id"] == "0"


@pytest.mark.asyncio
async def test_get_vector_not_real():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "ids": ["djjgkshdkhhdskhsdf"]
        }
        response = await ac.post("/vectors/get", json=payload, headers=HEADERS)
        print("Get Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert len(response.json()["results"]) == 0

@pytest.mark.asyncio
async def test_delete_vector():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "ids": ["0"]
        }
        response = await ac.post("/vectors/delete", json=payload, headers=HEADERS)
        print("Delete Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert "Deleted" in response.json()["message"]

        response = await ac.post("/vectors/get", json=payload, headers=HEADERS)
        print("Get Response:", response.status_code, response.text)
        assert response.status_code == 200
        assert len(response.json()["results"]) == 0





@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method", [
    ("/vectors/upsert", "GET"),
    ("/vectors/query", "GET"),
    ("/vectors/get", "GET"),
    ("/vectors/delete", "GET"),
])
async def test_method_not_allowed_vectors(endpoint, method):
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        url = f"http://test{API_PREFIX}{endpoint}"
        response = await getattr(ac, method.lower())(url, headers=HEADERS)
        assert response.status_code == 405


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,method,payload", [
    ("/vectors/upsert", "POST", {"index_name": INDEX_NAME, "index_key": INDEX_KEY, "items": [{"id": "1", "contents": "test"}]}),
    ("/vectors/query", "POST", {"index_name": INDEX_NAME, "index_key": INDEX_KEY, "query_contents": "test", "top_k": 1}),
    ("/vectors/get", "POST", {"index_name": INDEX_NAME, "index_key": INDEX_KEY, "ids": ["1"]}),
    ("/vectors/delete", "POST", {"index_name": INDEX_NAME, "index_key": INDEX_KEY, "ids": ["1"]}),
])
async def test_unauthorized_requests(endpoint, method, payload):
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        url = f"http://test{API_PREFIX}{endpoint}"
        if method == "POST":
            response = await ac.post(url, json=payload)
        elif method == "GET":
            response = await ac.get(url)
        assert response.status_code == 401
        assert response.json()["detail"] in ["API Key is required", "Invalid API Key"]


@pytest.mark.asyncio
async def test_vectors_upsert_invalid_json():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        headers = {"Content-Type": "application/json", **HEADERS}
        response = await ac.post("/vectors/upsert", content="{invalid json", headers=headers)
        assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_vectors_upsert_missing_fields():
    # Missing items
    payload = {
        "index_name": INDEX_NAME,
        "index_key": INDEX_KEY
    }
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        response = await ac.post("/vectors/upsert", json=payload, headers=HEADERS)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_query_response_format():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = {
            "index_name": INDEX_NAME,
            "index_key": INDEX_KEY,
            "query_contents": "test",
            "top_k": 1
        }
        response = await ac.post("/vectors/query", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        body = response.json()
        assert "results" in body
        assert isinstance(body["results"], list)


@pytest.mark.asyncio
async def test_concurrent_vector_queries():
    payload = {
        "index_name": INDEX_NAME,
        "index_key": INDEX_KEY,
        "query_contents": "test",
        "top_k": 1
    }
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        responses = await asyncio.gather(
            ac.post("/vectors/query", json=payload, headers=HEADERS),
            ac.post("/vectors/query", json=payload, headers=HEADERS),
            ac.post("/vectors/query", json=payload, headers=HEADERS)
        )
        for response in responses:
            assert response.status_code == 200
            assert "results" in response.json()

@pytest.mark.asyncio
async def test_delete_index():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=f"http://test{API_PREFIX}") as ac:
        payload = IndexOperationRequest(index_name=INDEX_NAME, index_key=INDEX_KEY).dict()
        response = await ac.post("/indexes/delete", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["status"] == "success"