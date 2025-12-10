# Unit tests for FastAPI content generation service
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# Test health check
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test content generation endpoint
def test_generate_content():
    payload = {
        "topic": "AI in education",
        "platform": "instagram",
        "tone": "satirical",
        "max_length": 280
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "platform" in data
    assert len(data["content"]) <= 280

# Test content refinement
def test_refine_content():
    payload = {
        "content": "Original content",
        "instruction": "Make it more satirical"
    }
    response = client.post("/refine", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "refined_content" in data

# Test batch generation
def test_batch_generation():
    payload = {
        "topics": ["AI", "education", "technology"],
        "platform": "twitter",
        "count": 3
    }
    response = client.post("/batch-generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["contents"]) == 3

# Test error handling
def test_invalid_payload():
    payload = {}
    response = client.post("/generate", json=payload)
    assert response.status_code == 422
