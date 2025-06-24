# backend/tests/test_exchange_offer_model.py
import pytest

# from datetime import datetime # Unused
from backend.app import create_app, db
from backend.app.models import User, UserProfile, Skill, ExchangeOffer, OfferStatusEnum


@pytest.fixture(scope="module")
def test_client_module():  # Renamed to avoid conflict if imported elsewhere
    flask_app = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test_secret_key_exchange",
        }
    )

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="function")
def init_database_session(test_client_module):  # test_client_module provides app context
    # Assuming test_client_module fixture ensures an app context is active.
    # We just need to clean DB for each function.
    db.session.remove()  # Close any existing session
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate tables for a clean state
    yield db  # Provide the db object
    db.session.remove()  # Clean up session after test


@pytest.fixture(scope="function")
def sample_user(init_database_session):
    user = User(username="testuser_offer", email="testoffer@example.com")
    user.set_password("password")
    profile = UserProfile(user=user, display_name=user.username)
    init_database_session.session.add(user)
    init_database_session.session.add(profile)
    init_database_session.session.flush()  # Changed commit to flush
    return user


@pytest.fixture(scope="function")
def sample_skill_offered(init_database_session):
    skill = Skill.query.filter_by(name="Skill Offered Test").first()
    if not skill:
        skill = Skill(name="Skill Offered Test")
        init_database_session.session.add(skill)
        init_database_session.session.flush()  # Changed commit to flush
    return skill


@pytest.fixture(scope="function")
def sample_skill_desired(init_database_session):
    skill = Skill.query.filter_by(name="Skill Desired Test").first()
    if not skill:
        skill = Skill(name="Skill Desired Test")
        init_database_session.session.add(skill)
        init_database_session.session.flush()  # Changed commit to flush
    return skill


def test_exchange_offer_creation_all_fields(
    init_database_session, sample_user, sample_skill_offered, sample_skill_desired
):
    """Test creating an ExchangeOffer with all fields populated."""
    offer_data = {
        "user_id": sample_user.id,
        "offered_skill_id": sample_skill_offered.id,
        "desired_skill_id": sample_skill_desired.id,
        "desired_description": "Looking for help with testing.",
        "description": "I can offer my expertise in model testing.",
        "status": OfferStatusEnum.ACTIVE,
        "location_preference": "Remote",
    }
    offer = ExchangeOffer(**offer_data)
    init_database_session.session.add(offer)
    init_database_session.session.commit()

    retrieved_offer = ExchangeOffer.query.get(offer.id)
    assert retrieved_offer is not None
    assert retrieved_offer.user_id == sample_user.id
    assert retrieved_offer.user == sample_user
    assert retrieved_offer.offered_skill_id == sample_skill_offered.id
    assert retrieved_offer.offered_skill == sample_skill_offered
    assert retrieved_offer.desired_skill_id == sample_skill_desired.id
    assert retrieved_offer.desired_skill == sample_skill_desired
    assert retrieved_offer.desired_description == "Looking for help with testing."
    assert retrieved_offer.description == "I can offer my expertise in model testing."
    assert retrieved_offer.status == OfferStatusEnum.ACTIVE
    assert retrieved_offer.location_preference == "Remote"
    assert retrieved_offer.created_at is not None
    assert (
        retrieved_offer.updated_at is not None
    )  # Should be populated by server_default/onupdate


def test_exchange_offer_creation_minimal_fields(
    init_database_session, sample_user, sample_skill_offered
):
    """Test creating an ExchangeOffer with only required and default fields."""
    offer = ExchangeOffer(
        user_id=sample_user.id,
        offered_skill_id=sample_skill_offered.id,
        desired_description="Anything useful in exchange.",
    )
    init_database_session.session.add(offer)
    init_database_session.session.commit()

    retrieved_offer = ExchangeOffer.query.get(offer.id)
    assert retrieved_offer is not None
    assert retrieved_offer.user_id == sample_user.id
    assert retrieved_offer.offered_skill_id == sample_skill_offered.id
    assert retrieved_offer.desired_description == "Anything useful in exchange."
    assert retrieved_offer.status == OfferStatusEnum.ACTIVE  # Default value
    assert retrieved_offer.desired_skill_id is None
    assert retrieved_offer.description is None
    assert retrieved_offer.location_preference is None


def test_exchange_offer_to_dict(
    init_database_session, sample_user, sample_skill_offered
):
    """Test the to_dict method of ExchangeOffer."""
    offer = ExchangeOffer(
        user_id=sample_user.id,
        offered_skill_id=sample_skill_offered.id,
        desired_description="Test to_dict",
        description="Detailed desc for dict",
        status=OfferStatusEnum.COMPLETED,
        location_preference="Local",
    )
    init_database_session.session.add(offer)
    init_database_session.session.commit()

    offer_dict = offer.to_dict()
    assert offer_dict["id"] == offer.id
    assert offer_dict["user_id"] == sample_user.id
    assert offer_dict["user"] == sample_user.username
    assert offer_dict["offered_skill_id"] == sample_skill_offered.id
    assert offer_dict["offered_skill_name"] == sample_skill_offered.name
    assert offer_dict["desired_skill_id"] is None
    assert offer_dict["desired_skill_name"] is None
    assert offer_dict["desired_description"] == "Test to_dict"
    assert offer_dict["description"] == "Detailed desc for dict"
    assert offer_dict["status"] == "completed"  # Enum value
    assert offer_dict["location_preference"] == "Local"
    assert offer_dict["created_at"] is not None
    assert offer_dict["updated_at"] is not None


def test_exchange_offer_relationships(
    init_database_session, sample_user, sample_skill_offered, sample_skill_desired
):
    """Test relationships are correctly established."""
    offer = ExchangeOffer(
        user=sample_user,  # Assigning object directly
        offered_skill=sample_skill_offered,
        desired_skill=sample_skill_desired,
        desired_description="Testing relationships",
    )
    init_database_session.session.add(offer)
    init_database_session.session.commit()

    retrieved_offer = ExchangeOffer.query.get(offer.id)
    assert retrieved_offer.user == sample_user
    assert retrieved_offer.offered_skill == sample_skill_offered
    assert retrieved_offer.desired_skill == sample_skill_desired
    assert sample_user.exchange_offers.count() >= 1  # Check backref
    assert sample_user.exchange_offers.filter_by(id=offer.id).first() is not None
    assert sample_skill_offered.offers_made.count() >= 1
    assert sample_skill_desired.offers_desired.count() >= 1


def test_exchange_offer_repr(init_database_session, sample_user, sample_skill_offered):
    """Test the __repr__ method."""
    offer = ExchangeOffer(
        user_id=sample_user.id,
        offered_skill_id=sample_skill_offered.id,
        desired_description="Repr test",
    )
    init_database_session.session.add(offer)
    init_database_session.session.commit()  # Commit for ID
    expected_repr = f"<ExchangeOffer id={offer.id} user_id={sample_user.id} offered_skill_id={sample_skill_offered.id} status='active'>"
    assert repr(offer) == expected_repr


# Potential IntegrityError tests (foreign key constraints)
def test_exchange_offer_missing_user_fk_constraint(
    init_database_session, sample_skill_offered
):
    """Test FK constraint for user_id."""
    offer = ExchangeOffer(
        user_id=99999,  # Non-existent user
        offered_skill_id=sample_skill_offered.id,
        desired_description="FK test",
    )
    init_database_session.session.add(offer)
    with pytest.raises(Exception):  # sqlalchemy.exc.IntegrityError
        init_database_session.session.flush() # Try to trigger error before commit
        init_database_session.session.commit() # This should definitely fail
    init_database_session.session.rollback()


def test_exchange_offer_missing_skill_fk_constraint(init_database_session, sample_user):
    """Test FK constraint for offered_skill_id."""
    offer = ExchangeOffer(
        user_id=sample_user.id,
        offered_skill_id=99999,  # Non-existent skill
        desired_description="FK test skill",
    )
    init_database_session.session.add(offer)
    with pytest.raises(Exception):  # sqlalchemy.exc.IntegrityError
        init_database_session.session.flush() # Try to trigger error before commit
        init_database_session.session.commit() # This should definitely fail
    init_database_session.session.rollback()
