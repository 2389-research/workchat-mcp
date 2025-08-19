# ABOUTME: Basic application tests
# ABOUTME: Tests FastAPI app endpoints and core functionality

from fastapi.testclient import TestClient

from workchat.app import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from WorkChat!"}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
