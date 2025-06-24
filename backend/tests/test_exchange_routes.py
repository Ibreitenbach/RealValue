# backend/tests/test_exchange_routes.py
import pytest

# import json # Unused
from backend.app import create_app, db
from backend.app.models import User, UserProfile, Skill, ExchangeOffer, OfferStatusEnum
import jwt  # PyJWT for generating test tokens
import time
import os

# Use a consistent SECRET_KEY for tests, matching what utils.auth might expect
TEST_SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_if_not_set")


@pytest.fixture(scope="module")
def test_app_module_scope():
    flask_app = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": TEST_SECRET_KEY,  # Ensure this matches token generation
            "JWT_SECRET_KEY": TEST_SECRET_KEY,  # For Flask-JWT-Extended if used elsewhere
        }
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app  # Yield the app for direct use if needed
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="module")
def test_client(test_app_module_scope):
    with test_app_module_scope.test_client() as testing_client:
        yield testing_client


@pytest.fixture(scope="function")
def init_db_function_scope(test_app_module_scope):  # test_app_module_scope is the app, already in context
    # Assuming test_app_module_scope fixture ensures an app context is active
    # for the duration of the module. We just need to clean DB for each function.
    db.session.remove()  # Close any existing session
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate tables for a clean state
    yield db  # Provide the db object
    db.session.remove()  # Clean up session after test


# --- Test Users and Auth ---
@pytest.fixture(scope="function")
def test_user1(init_db_function_scope):
    user = User.query.filter_by(email="user1_exchange@example.com").first()
    if not user:
        user = User(username="user1_exchange", email="user1_exchange@example.com")
        user.set_password("password123")
        profile = UserProfile(user=user, display_name=user.username)
        init_db_function_scope.session.add(user)
        init_db_function_scope.session.add(profile)
        init_db_function_scope.session.flush()  # Flush to get IDs
    return user


@pytest.fixture(scope="function")
def test_user2(init_db_function_scope):
    user = User.query.filter_by(email="user2_exchange@example.com").first()
    if not user:
        user = User(username="user2_exchange", email="user2_exchange@example.com")
        user.set_password("password456")
        profile = UserProfile(user=user, display_name=user.username)
        init_db_function_scope.session.add(user)
        init_db_function_scope.session.add(profile)
        init_db_function_scope.session.flush()  # Flush to get IDs
    return user


def generate_auth_token(user_id):
    """Generates a JWT token for a given user_id for @token_required decorator."""
    payload = {"user_id": user_id, "exp": time.time() + 3600}  # Expires in 1 hour
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")


@pytest.fixture(scope="function")
def auth_headers_user1(test_user1):
    token = generate_auth_token(test_user1.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_user2(test_user2):
    token = generate_auth_token(test_user2.id)
    return {"Authorization": f"Bearer {token}"}


# --- Test Skills ---
@pytest.fixture(scope="function")
def skill1(init_db_function_scope):
    skill = Skill.query.filter_by(name="Test Skill Alpha").first()
    if not skill:
        skill = Skill(name="Test Skill Alpha")
        init_db_function_scope.session.add(skill)
        init_db_function_scope.session.flush()
    return skill


@pytest.fixture(scope="function")
def skill2(init_db_function_scope):
    skill = Skill.query.filter_by(name="Test Skill Beta").first()
    if not skill:
        skill = Skill(name="Test Skill Beta")
        init_db_function_scope.session.add(skill)
        init_db_function_scope.session.flush()
    return skill


# --- Test Exchange Offers ---
@pytest.fixture(scope="function")
def sample_offer_user1_active(init_db_function_scope, test_user1, skill1, skill2):
    offer = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_skill_id=skill2.id,
        desired_description="Need Beta skill",
        description="Offering Alpha skill",
        status=OfferStatusEnum.ACTIVE,
        location_preference="Remote",
    )
    init_db_function_scope.session.add(offer)
    init_db_function_scope.session.flush()  # Flush, rely on test-level rollback
    return offer


@pytest.fixture(scope="function")
def sample_offer_user2_completed(init_db_function_scope, test_user2, skill2, skill1):
    offer = ExchangeOffer(
        user_id=test_user2.id,
        offered_skill_id=skill2.id,
        desired_skill_id=skill1.id,
        desired_description="Need Alpha skill",
        description="Offering Beta skill for completed deal",
        status=OfferStatusEnum.COMPLETED,
        location_preference="Local",
    )
    init_db_function_scope.session.add(offer)
    init_db_function_scope.session.flush()  # Flush, rely on test-level rollback
    return offer


# ==== POST /api/exchange_offers ====
def test_create_exchange_offer_success(
    test_client, test_user1, auth_headers_user1, skill1, skill2, init_db_function_scope
): # Added test_user1
    data = {
        "offered_skill_id": skill1.id,
        "desired_skill_id": skill2.id,
        "desired_description": "Looking for Skill Beta expertise.",
        "description": "I can provide Skill Alpha services.",
        "location_preference": "Remote",
        "status": "active",
    }
    response = test_client.post(
        "/api/exchange_offers", headers=auth_headers_user1, json=data
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["offered_skill_id"] == skill1.id
    assert json_data["desired_skill_id"] == skill2.id
    assert json_data["desired_description"] == "Looking for Skill Beta expertise."
    assert json_data["status"] == "active"
    print(f"DEBUG: test_user1 type: {type(test_user1)}, value: {test_user1}")
    if hasattr(test_user1, 'id'):
        print(f"DEBUG: test_user1.id: {test_user1.id}")
    else:
        print("DEBUG: test_user1 has no id attribute")
    assert json_data["user_id"] == test_user1.id  # Check if user_id is correctly set


def test_create_exchange_offer_missing_fields(test_client, auth_headers_user1, skill1):
    data = {"offered_skill_id": skill1.id}  # Missing desired_description
    response = test_client.post(
        "/api/exchange_offers", headers=auth_headers_user1, json=data
    )
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["message"]


def test_create_exchange_offer_invalid_skill_id(test_client, auth_headers_user1):
    data = {
        "offered_skill_id": 9999,  # Invalid skill
        "desired_description": "Test desc.",
    }
    response = test_client.post(
        "/api/exchange_offers", headers=auth_headers_user1, json=data
    )
    assert response.status_code == 404  # Skill not found
    assert "Offered skill with id 9999 not found" in response.get_json()["message"]


def test_create_exchange_offer_no_auth(test_client, skill1):
    data = {"offered_skill_id": skill1.id, "desired_description": "Test"}
    response = test_client.post("/api/exchange_offers", json=data)
    assert response.status_code == 401  # Token is missing


# ==== GET /api/exchange_offers ====
def test_get_exchange_offers_success(
    test_client,
    auth_headers_user1,
    sample_offer_user1_active,
    sample_offer_user2_completed,
):
    # sample_offer_user2_completed is not active, so should not be returned by default
    response = test_client.get("/api/exchange_offers", headers=auth_headers_user1)
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data["offers"]) >= 1  # At least sample_offer_user1_active
    # Ensure only active offers are returned by default
    assert all(offer["status"] == "active" for offer in json_data["offers"])
    found_offer_ids = [offer["id"] for offer in json_data["offers"]]
    assert sample_offer_user1_active.id in found_offer_ids
    assert sample_offer_user2_completed.id not in found_offer_ids


def test_get_exchange_offers_filter_offered_skill(
    test_client, auth_headers_user1, skill1, skill2, init_db_function_scope, test_user1
):
    # Create specific offers for filtering
    ExchangeOffer.query.delete()  # Clear previous offers for clean filter test
    offer1 = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_description="Desc 1",
        status=OfferStatusEnum.ACTIVE,
    )
    offer2 = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill2.id,
        desired_description="Desc 2",
        status=OfferStatusEnum.ACTIVE,
    )
    init_db_function_scope.session.add_all([offer1, offer2])
    init_db_function_scope.session.commit()

    response = test_client.get(
        f"/api/exchange_offers?offered_skill_id={skill1.id}", headers=auth_headers_user1
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data["offers"]) == 1
    assert json_data["offers"][0]["offered_skill_id"] == skill1.id
    assert json_data["offers"][0]["id"] == offer1.id


def test_get_exchange_offers_search(
    test_client,
    auth_headers_user1,
    sample_offer_user1_active,
    init_db_function_scope,
    test_user1,
    skill1,
):
    # sample_offer_user1_active has "Offering Alpha skill" in description and "Need Beta skill" in desired_description
    # skill1 is "Test Skill Alpha"
    response = test_client.get(
        "/api/exchange_offers?search=Alpha", headers=auth_headers_user1
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data["offers"]) >= 1
    assert sample_offer_user1_active.id in [o["id"] for o in json_data["offers"]]

    response_beta = test_client.get(
        "/api/exchange_offers?search=Beta", headers=auth_headers_user1
    )
    assert response_beta.status_code == 200
    json_data_beta = response_beta.get_json()
    assert len(json_data_beta["offers"]) >= 1
    assert sample_offer_user1_active.id in [o["id"] for o in json_data_beta["offers"]]

    response_nomatch = test_client.get(
        "/api/exchange_offers?search=ZuluEchoXray", headers=auth_headers_user1
    )
    assert response_nomatch.status_code == 200
    json_data_nomatch = response_nomatch.get_json()
    assert len(json_data_nomatch["offers"]) == 0


# ==== GET /api/exchange_offers/<id> ====
def test_get_exchange_offer_detail_success(
    test_client, auth_headers_user1, sample_offer_user1_active
):
    response = test_client.get(
        f"/api/exchange_offers/{sample_offer_user1_active.id}",
        headers=auth_headers_user1,
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["id"] == sample_offer_user1_active.id
    assert json_data["description"] == sample_offer_user1_active.description


def test_get_exchange_offer_detail_not_found(test_client, auth_headers_user1):
    response = test_client.get("/api/exchange_offers/99999", headers=auth_headers_user1)
    assert response.status_code == 404


# ==== PUT /api/exchange_offers/<id> ====
def test_update_exchange_offer_success(
    test_client, auth_headers_user1, sample_offer_user1_active, skill2
):
    update_data = {
        "description": "Updated description for Alpha skill",
        "desired_skill_id": skill2.id,  # Keep same desired skill or change
        "status": "matched",
    }
    response = test_client.put(
        f"/api/exchange_offers/{sample_offer_user1_active.id}",
        headers=auth_headers_user1,
        json=update_data,
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["description"] == "Updated description for Alpha skill"
    assert json_data["status"] == "matched"
    assert json_data["desired_skill_id"] == skill2.id


def test_update_exchange_offer_unauthorized(
    test_client, auth_headers_user2, sample_offer_user1_active
):
    # user2 tries to update user1's offer
    update_data = {"description": "Attempted unauthorized update"}
    response = test_client.put(
        f"/api/exchange_offers/{sample_offer_user1_active.id}",
        headers=auth_headers_user2,
        json=update_data,
    )
    assert response.status_code == 403


def test_update_exchange_offer_not_found(test_client, auth_headers_user1):
    update_data = {"description": "Update non-existent offer"}
    response = test_client.put(
        "/api/exchange_offers/99999", headers=auth_headers_user1, json=update_data
    )
    assert response.status_code == 404


def test_update_exchange_offer_invalid_status(
    test_client, auth_headers_user1, sample_offer_user1_active
):
    update_data = {"status": "invalid_status_value"}
    response = test_client.put(
        f"/api/exchange_offers/{sample_offer_user1_active.id}",
        headers=auth_headers_user1,
        json=update_data,
    )
    assert response.status_code == 400
    assert "Invalid status" in response.get_json()["message"]


# ==== DELETE /api/exchange_offers/<id> ====
def test_delete_exchange_offer_success(
    test_client, auth_headers_user1, sample_offer_user1_active, init_db_function_scope
):
    offer_id_to_delete = sample_offer_user1_active.id
    response = test_client.delete(
        f"/api/exchange_offers/{offer_id_to_delete}", headers=auth_headers_user1
    )
    assert response.status_code == 200
    assert "Exchange offer deleted successfully" in response.get_json()["message"]
    # Verify it's actually deleted
    deleted_offer = init_db_function_scope.session.get(
        ExchangeOffer, offer_id_to_delete
    )
    assert deleted_offer is None


def test_delete_exchange_offer_unauthorized(
    test_client, auth_headers_user2, sample_offer_user1_active
):
    response = test_client.delete(
        f"/api/exchange_offers/{sample_offer_user1_active.id}",
        headers=auth_headers_user2,
    )
    assert response.status_code == 403


def test_delete_exchange_offer_not_found(test_client, auth_headers_user1):
    response = test_client.delete(
        "/api/exchange_offers/99999", headers=auth_headers_user1
    )
    assert response.status_code == 404


# ==== GET /api/users/me/exchange_offers ====
def test_get_my_exchange_offers_success(
    test_client, auth_headers_user1, test_user1, skill1, init_db_function_scope
):
    # Clear existing offers to ensure clean slate for this user
    ExchangeOffer.query.filter_by(user_id=test_user1.id).delete()
    init_db_function_scope.session.commit()

    offer1 = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_description="My Offer 1",
        status=OfferStatusEnum.ACTIVE,
    )
    offer2 = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_description="My Offer 2",
        status=OfferStatusEnum.COMPLETED,
    )
    init_db_function_scope.session.add_all([offer1, offer2])
    init_db_function_scope.session.commit()

    response = test_client.get(
        "/api/users/me/exchange_offers", headers=auth_headers_user1
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert (
        len(json_data["offers"]) == 2
    )  # Should get all regardless of status by default for "me"
    offer_ids = {offer["id"] for offer in json_data["offers"]}
    assert offer1.id in offer_ids
    assert offer2.id in offer_ids


def test_get_my_exchange_offers_filter_status(
    test_client, auth_headers_user1, test_user1, skill1, init_db_function_scope
):
    ExchangeOffer.query.filter_by(user_id=test_user1.id).delete()
    init_db_function_scope.session.commit()

    offer_active = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_description="My Active Offer",
        status=OfferStatusEnum.ACTIVE,
    )
    offer_completed = ExchangeOffer(
        user_id=test_user1.id,
        offered_skill_id=skill1.id,
        desired_description="My Completed Offer",
        status=OfferStatusEnum.COMPLETED,
    )
    init_db_function_scope.session.add_all([offer_active, offer_completed])
    init_db_function_scope.session.commit()

    response = test_client.get(
        "/api/users/me/exchange_offers?status=active", headers=auth_headers_user1
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data["offers"]) == 1
    assert json_data["offers"][0]["id"] == offer_active.id
    assert json_data["offers"][0]["status"] == "active"


def test_get_my_exchange_offers_no_offers(
    test_client, auth_headers_user2, test_user2, init_db_function_scope
):
    # Ensure user2 has no offers
    ExchangeOffer.query.filter_by(user_id=test_user2.id).delete()
    init_db_function_scope.session.commit()

    response = test_client.get(
        "/api/users/me/exchange_offers", headers=auth_headers_user2
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data["offers"]) == 0
    assert json_data["total"] == 0


def test_get_my_exchange_offers_no_auth(test_client):
    response = test_client.get("/api/users/me/exchange_offers")
    assert response.status_code == 401  # Token is missing
    assert "Token is missing" in response.get_json()["message"]
