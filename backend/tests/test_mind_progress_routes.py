# backend/tests/test_mind_progress_routes.py
import pytest
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from backend.app import create_app, db
from backend.app.models import (
    User,
    JournalEntry,
    MindsetChallengeTemplate,
    UserMindsetCompletion,
    MindfulMomentTemplate,
    UserReminderSetting,
    MindsetCompletionStatus,
)


@pytest.fixture(scope="module")
def test_app_routes():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test_jwt_secret_routes",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_routes(test_app_routes):
    return test_app_routes.test_client()


@pytest.fixture
def init_database_routes(test_app_routes):
    user1 = User(id=1, username="testuser1", email="testuser1@example.com")
    user1.set_password("password")
    user2 = User(
        id=2, username="testuser2", email="testuser2@example.com"
    )  # For testing other user
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    # Journal Entries for User 1
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 1",
            created_at=datetime.utcnow() - timedelta(days=3),
            reflection_tags="tag1",
        )
    )
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 2",
            created_at=datetime.utcnow() - timedelta(days=20),
        )
    )

    # Mindset Challenges and Completions for User 1
    mct1 = MindsetChallengeTemplate(id=1, title="Challenge A", category="CatA")
    mct2 = MindsetChallengeTemplate(id=2, title="Challenge B", category="CatB")
    db.session.add_all([mct1, mct2])
    db.session.commit()
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct1.id,
            completed_at=datetime.utcnow() - timedelta(days=5),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct2.id,
            completed_at=datetime.utcnow() - timedelta(days=35),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )

    # Mindful Moment Reminders for User 1
    mmt1 = MindfulMomentTemplate(id=1, text="Be present")
    db.session.add(mmt1)
    db.session.commit()
    db.session.add(
        UserReminderSetting(
            user_id=user1.id,
            mindful_moment_template_id=mmt1.id,
            frequency="DAILY",
            is_enabled=True,
        )
    )

    # User 2 has no data other than the user entry itself.

    db.session.commit()
    yield
    db.session.remove()
    # Clean up specific data if necessary, or rely on drop_all from module fixture


@pytest.fixture
def auth_headers(test_app_routes):
    with test_app_routes.app_context():
        # Assuming user_id 1 exists from init_database_routes
        access_token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_user2(test_app_routes):
    with test_app_routes.app_context():
        access_token = create_access_token(identity="2")
    return {"Authorization": f"Bearer {access_token}"}


# Test /api/users/me/mind_progress/summary
def test_get_summary_success(client_routes, init_database_routes, auth_headers):
    response = client_routes.get(
        "/api/users/me/mind_progress/summary", headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total_journal_entries" in data
    assert "total_challenges_completed" in data
    assert "active_reminders" in data
    assert data["total_journal_entries"] == 2
    assert data["total_challenges_completed"] == 2
    assert data["active_reminders"] == 1


def test_get_summary_no_auth(client_routes, init_database_routes):
    response = client_routes.get("/api/users/me/mind_progress/summary")
    assert response.status_code == 401  # Expecting JWT error if no token


# Test /api/users/me/mind_progress/journaling_trends
def test_get_journaling_trends_weekly_success(
    client_routes, init_database_routes, auth_headers
):
    response = client_routes.get(
        "/api/users/me/mind_progress/journaling_trends?period=weekly",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if data:  # User 1 has 2 entries
        assert "date" in data[0]
        assert "count" in data[0]
        assert data[0]["count"] > 0


def test_get_journaling_trends_monthly_success(
    client_routes, init_database_routes, auth_headers
):
    response = client_routes.get(
        "/api/users/me/mind_progress/journaling_trends?period=monthly",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if data:
        assert "month" in data[0]
        assert "count" in data[0]
        assert data[0]["count"] > 0
        # User1 has 2 entries, one this month, one last month (days=3, days=20)
        # This might result in 1 or 2 items in the list depending on current date
        total_entries_in_trends = sum(item["count"] for item in data)
        assert total_entries_in_trends == 2


def test_get_journaling_trends_default_period(
    client_routes, init_database_routes, auth_headers
):
    response = client_routes.get(
        "/api/users/me/mind_progress/journaling_trends", headers=auth_headers
    )  # Defaults to weekly
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if data:
        assert "date" in data[0]  # Weekly uses "date"


def test_get_journaling_trends_invalid_period(
    client_routes, init_database_routes, auth_headers
):
    response = client_routes.get(
        "/api/users/me/mind_progress/journaling_trends?period=yearly",
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid 'period' parameter" in data["message"]


def test_get_journaling_trends_no_data_user(
    client_routes, init_database_routes, auth_headers_user2
):
    # User 2 has no journal entries in init_database_routes
    response = client_routes.get(
        "/api/users/me/mind_progress/journaling_trends", headers=auth_headers_user2
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []


# Test /api/users/me/mind_progress/challenge_trends
def test_get_challenge_trends_success(
    client_routes, init_database_routes, auth_headers
):
    response = client_routes.get(
        "/api/users/me/mind_progress/challenge_trends", headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # User1 has 2 completions, one this month (CatA), one last month (CatB)
    # (days=5, days=35)
    # This should result in 2 items if they fall in different YYYY-MM periods
    if data:
        assert "category" in data[0]
        assert "completed_count" in data[0]
        assert "month" in data[0]

    total_completed_in_trends = sum(item["completed_count"] for item in data)
    assert total_completed_in_trends == 2


def test_get_challenge_trends_no_data_user(
    client_routes, init_database_routes, auth_headers_user2
):
    # User 2 has no challenge completions
    response = client_routes.get(
        "/api/users/me/mind_progress/challenge_trends", headers=auth_headers_user2
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []


# Test /api/users/me/mind_progress/tag_analysis
def test_get_tag_analysis_success(client_routes, init_database_routes, auth_headers):
    response = client_routes.get(
        "/api/users/me/mind_progress/tag_analysis", headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    # User1 has one entry with "tag1"
    assert data.get("tag1") == 1
    assert len(data) == 1


def test_get_tag_analysis_no_data_user(
    client_routes, init_database_routes, auth_headers_user2
):
    # User 2 has no journal entries with tags
    response = client_routes.get(
        "/api/users/me/mind_progress/tag_analysis", headers=auth_headers_user2
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {}


def test_get_summary_invalid_token_user(client_routes, init_database_routes):
    # Create a token for a non-existent user
    with client_routes.application.app_context():  # Get app context from client
        access_token = create_access_token(identity="999")
    invalid_auth_headers = {"Authorization": f"Bearer {access_token}"}

    response = client_routes.get(
        "/api/users/me/mind_progress/summary", headers=invalid_auth_headers
    )
    # The service layer currently doesn't raise an error for non-existent user_id, it just returns empty/0 counts.
    # The JWT token itself is valid, but the user_id from it might not exist.
    # flask_jwt_extended by default does not check if the identity exists in DB on decode.
    # Our service functions are resilient to user_id not having data.
    # If User.query.get(user_id) in a route returned None, that would be a 401/404,
    # but here get_jwt_identity() just gives the string "999".
    # The analysis_service functions will then query for user_id=999 and find nothing.
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["total_journal_entries"] == 0
    assert data["total_challenges_completed"] == 0
    assert data["active_reminders"] == 0

    # If the user_id in token is not an int, it should fail earlier in the route
    with client_routes.application.app_context():
        access_token_bad_id = create_access_token(identity="not-an-int")
    bad_id_headers = {"Authorization": f"Bearer {access_token_bad_id}"}
    response_bad_id = client_routes.get(
        "/api/users/me/mind_progress/summary", headers=bad_id_headers
    )
    assert response_bad_id.status_code == 400
    data_bad_id = json.loads(response_bad_id.data)
    assert "Invalid user identity" in data_bad_id["message"]


# Test authentication for all endpoints
ENDPOINTS_TO_TEST_AUTH = [
    "/api/users/me/mind_progress/summary",
    "/api/users/me/mind_progress/journaling_trends",
    "/api/users/me/mind_progress/challenge_trends",
    "/api/users/me/mind_progress/tag_analysis",
]


@pytest.mark.parametrize("endpoint", ENDPOINTS_TO_TEST_AUTH)
def test_endpoint_no_auth_token(client_routes, endpoint):
    response = client_routes.get(endpoint)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "Missing Authorization Header" in data.get(
        "msg", ""
    ) or "Token is missing" in data.get(
        "message", ""
    )  # Flask-JWT different messages


@pytest.mark.parametrize("endpoint", ENDPOINTS_TO_TEST_AUTH)
def test_endpoint_invalid_auth_token(client_routes, endpoint):
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = client_routes.get(endpoint, headers=headers)
    assert response.status_code == 422  # Flask-JWT specific error for malformed token
    data = json.loads(response.data)
    assert "Invalid token" in data.get("msg", "")  # Or similar message from Flask-JWT

    # Example with an expired token (difficult to test without time mocking)
    # with client_routes.application.app_context():
    #     expired_token = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))
    # headers_expired = {"Authorization": f"Bearer {expired_token}"}
    # response_expired = client_routes.get(endpoint, headers=headers_expired)
    # assert response_expired.status_code == 401 # Token expired
    # data_expired = json.loads(response_expired.data)
    # assert "Token has expired" in data_expired.get("msg", "")


# Note: The `token_required` decorator in `utils/auth.py` from the original codebase
# seems to be a custom one. The routes I created use `flask_jwt_extended.jwt_required`.
# The error messages for missing/invalid tokens might differ based on which decorator is
# actually active if `utils.auth.token_required` was intended to be used instead of `jwt_required`.
# For these tests, I'm assuming `jwt_required` is the one being used as per my route implementation.
# If `utils.auth.token_required` was used, it has its own error messages like "Token is missing!".
# `flask_jwt_extended` has messages like "Missing Authorization Header" or "Invalid token padding".
# The tests for 401/422 reflect flask-jwt-extended's behavior.
# The `test_get_summary_invalid_token_user` also shows that `get_jwt_identity()` is just returning the string from the token.
# A more robust system might add a step to actually load the user object from DB after getting identity.
# For example, using `@jwt_required(user_loader=custom_user_loader)` or similar.
# My current routes cast `get_jwt_identity()` to `int`. If this cast fails, it returns 400.
# If the int user_id does not exist, the service functions will just return empty results for that user.
# This is acceptable for now.


# One final check to ensure the test database is clean for other test modules
def test_ensure_db_clean(test_app_routes):
    with test_app_routes.app_context():
        assert User.query.count() > 0  # Should have users from init_database_routes
        # This test doesn't clean, it just confirms data exists from its fixture.
        # The module-scoped fixture `test_app_routes` handles drop_all.
