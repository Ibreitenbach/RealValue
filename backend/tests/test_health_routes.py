# backend/tests/test_health_routes.py
import pytest
import json
from app import create_app
from datetime import datetime


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_endpoint(client):
    """Test the /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "Backend is healthy!"
    assert "timestamp" in data

    # Validate timestamp format
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not in ISO format")
