"""
Main Application Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Apex Workspace Management API" in data["message"]


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Apex Workspace Management API" in data["message"]


@pytest.mark.asyncio
async def test_docs_endpoint(client: AsyncClient):
    """Test API documentation endpoint"""
    response = await client.get("/docs")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_openapi_endpoint(client: AsyncClient):
    """Test OpenAPI schema endpoint"""
    response = await client.get("/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Apex Workspace Management API"