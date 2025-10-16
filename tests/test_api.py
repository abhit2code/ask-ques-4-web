import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG Engine API is running"}

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ingest_url_invalid():
    """Test URL ingestion with invalid URL"""
    response = client.post("/api/ingest-url", json={"url": "invalid-url"})
    assert response.status_code == 422  # Validation error

def test_query_empty():
    """Test query with empty string"""
    response = client.post("/api/query", json={"query": ""})
    assert response.status_code == 400
