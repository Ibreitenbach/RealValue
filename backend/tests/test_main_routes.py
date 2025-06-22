# backend/tests/test_main_routes.py
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            # Any test specific setup, e.g., create test database
            pass
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the RealValue Backend API!" in response.data


def test_status_page(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert b"Backend is running!" in response.data
