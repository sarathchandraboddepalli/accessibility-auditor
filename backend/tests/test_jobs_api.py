import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_jobs_empty(client):
    response = await client.get("/api/v1/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_job(client):
    response = await client.post("/api/v1/jobs/", json={
        "url": "https://example.com",
        "site_name": "Example Gov",
        "max_pages": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["status"] in ("pending", "running", "completed", "failed")
