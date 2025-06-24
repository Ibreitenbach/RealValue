import pytest
import json
from app import create_app, db
from app.models import User, UserProfile
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="function")  # Changed scope to function for db isolation
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"  # Use in-memory DB for tests
    )
    app.config["JWT_SECRET_KEY"] = "test_jwt_secret_key"  # Consistent JWT key for tests
    # Disable CSRF protection in tests if it's enabled and not handled
    # app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()  # Create tables for each test
        yield app.test_client()  # Use app.test_client()
        db.session.remove()  # Ensure session is closed
        db.drop_all()  # Drop tables after each test


# Helper function to register a user and return user object and auth token
def register_user(client, username, email, password):
    response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    return User.query.filter_by(username=username).first(), data["access_token"]


# --- Test User Registration and Profile Creation ---
def test_register_creates_profile(client):
    user, _ = register_user(client, "testuser1", "test1@example.com", "password123")

    assert user is not None
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    assert profile is not None
    assert profile.display_name == "testuser1"  # Default display name
    assert profile.bio == ""  # Default empty bio


# --- Tests for GET /api/profile/me ---
def test_get_my_profile_unauthenticated(client):
    response = client.get("/api/profile/me")
    assert response.status_code == 401  # Expecting JWT Required


def test_get_my_profile_authenticated_existing_profile(client):
    user, token = register_user(client, "testuser2", "test2@example.com", "password123")

    # Profile should have been created on registration
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/profile/me", headers=headers)
    print(
        "Response data for test_get_my_profile_authenticated_existing_profile:",
        response.data,
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user_id"] == user.id
    assert data["display_name"] == user.username
    assert data["bio"] == ""


def test_get_my_profile_creates_if_not_exists(client):
    # Simulate a user existing without a profile (e.g. legacy user)
    # This requires manually creating a user without triggering the registration hook that creates a profile.
    # Or, more simply, test the auto-creation if a profile is manually deleted after registration.

    user = User(username="legacyuser", email="legacy@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Manually ensure no profile exists (though user.profile relationship should be None)
    assert UserProfile.query.filter_by(user_id=user.id).first() is None

    # Log in this legacy user
    login_response = client.post(
        "/api/auth/login", json={"username": "legacyuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = json.loads(login_response.data)["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user_id"] == user.id
    assert data["display_name"] == user.username  # Default created
    assert data["bio"] == ""

    # Verify profile was indeed created in DB
    profile_db = UserProfile.query.filter_by(user_id=user.id).first()
    assert profile_db is not None
    assert profile_db.display_name == user.username


# --- Tests for PUT /api/profile/me ---
def test_update_my_profile_unauthenticated(client):
    response = client.put("/api/profile/me", json={"display_name": "New Name"})
    assert response.status_code == 401


def test_update_my_profile_authenticated_valid_data(client):
    _, token = register_user(client, "testuser3", "test3@example.com", "password123")

    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"display_name": "Updated Name", "bio": "This is my new bio."}
    response = client.put("/api/profile/me", headers=headers, json=update_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["display_name"] == "Updated Name"
    assert data["bio"] == "This is my new bio."

    # Verify in DB
    user = User.query.filter_by(username="testuser3").first()
    profile_db = UserProfile.query.filter_by(user_id=user.id).first()
    assert profile_db.display_name == "Updated Name"
    assert profile_db.bio == "This is my new bio."


def test_update_my_profile_partial_data(client):
    user, token = register_user(client, "testuser4", "test4@example.com", "password123")

    headers = {"Authorization": f"Bearer {token}"}
    # Update only display_name
    update_data_name = {"display_name": "Just Name Change"}
    response_name = client.put(
        "/api/profile/me", headers=headers, json=update_data_name
    )
    assert response_name.status_code == 200
    data_name = json.loads(response_name.data)
    assert data_name["display_name"] == "Just Name Change"
    assert data_name["bio"] == ""  # Bio should remain as default

    # Update only bio
    update_data_bio = {"bio": "Just Bio Change"}
    response_bio = client.put("/api/profile/me", headers=headers, json=update_data_bio)
    assert response_bio.status_code == 200
    data_bio = json.loads(response_bio.data)
    assert (
        data_bio["display_name"] == "Just Name Change"
    )  # Name should persist from previous update
    assert data_bio["bio"] == "Just Bio Change"


def test_update_my_profile_empty_json(client):
    _, token = register_user(client, "testuser5", "test5@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/api/profile/me", headers=headers, data="{}", content_type="application/json"
    )  # Empty JSON
    assert (
        response.status_code == 200
    )  # Should succeed, making no changes or using defaults
    # The current implementation allows empty JSON and makes no changes, which is acceptable.
    # If specific error for empty non-null fields was required, API would need adjustment.


def test_update_my_profile_no_json_body(client):
    _, token = register_user(client, "testuser6", "test6@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("/api/profile/me", headers=headers)  # No JSON body
    assert response.status_code == 400  # Expecting 'Invalid or missing JSON in request'
    data = json.loads(response.data)
    assert (
        "Invalid or missing JSON in request" in data["msg"]
    )  # Updated expected message


def test_update_my_profile_ensure_other_user_profile_not_affected(client):
    user1, token1 = register_user(client, "userOne", "userone@example.com", "pass1")
    user2, token2 = register_user(client, "userTwo", "usertwo@example.com", "pass2")

    # Update userOne's profile
    headers1 = {"Authorization": f"Bearer {token1}"}
    update_data1 = {"display_name": "User One New Name", "bio": "Bio for User One"}
    client.put("/api/profile/me", headers=headers1, json=update_data1)

    # Check userTwo's profile remains unchanged
    profile2_before_access = UserProfile.query.filter_by(user_id=user2.id).first()
    assert profile2_before_access.display_name == "userTwo"  # Original display name
    assert profile2_before_access.bio == ""  # Original bio

    # Access userTwo's profile via API (should be unchanged)
    headers2 = {"Authorization": f"Bearer {token2}"}
    response2 = client.get("/api/profile/me", headers=headers2)
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2["display_name"] == "userTwo"
    assert data2["bio"] == ""

    # Verify userOne's profile is indeed updated
    profile1_after_update = UserProfile.query.filter_by(user_id=user1.id).first()
    assert profile1_after_update.display_name == "User One New Name"
    assert profile1_after_update.bio == "Bio for User One"


# A test for the login endpoint ensuring profile creation if missing
def test_login_creates_profile_if_not_exists(client):
    # Manually create a user without a profile
    user = User(username="loginuser", email="login@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    assert (
        UserProfile.query.filter_by(user_id=user.id).first() is None
    )  # Ensure no profile

    # Log in this user
    login_response = client.post(
        "/api/auth/login", json={"username": "loginuser", "password": "password123"}
    )
    assert login_response.status_code == 200

    # Verify profile was created in DB by the login endpoint
    profile_db = UserProfile.query.filter_by(user_id=user.id).first()
    assert profile_db is not None
    assert profile_db.display_name == user.username
    assert profile_db.bio == ""

    # Also check that accessing GET /me returns this new profile
    token = json.loads(login_response.data)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["display_name"] == user.username
    assert data["bio"] == ""
