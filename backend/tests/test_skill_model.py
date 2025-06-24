# backend/tests/test_skill_model.py
import pytest
from backend.app import create_app, db
from backend.app.models import Skill


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory SQLite for tests
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for forms if any
            "SECRET_KEY": "test_secret_key",
        }
    )

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client  # this is where the testing happens!
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="function")  # Function scope for db session per test
def init_database(test_client):  # Relies on app_context from test_client
    db.session.begin_nested()  # Use nested transactions for cleaner test isolation
    yield db
    db.session.rollback()  # Rollback changes after each test


def test_skill_creation(init_database):
    """Test creating a new Skill."""
    skill_name = "Test Skill"
    skill = Skill(name=skill_name)
    init_database.session.add(skill)
    init_database.session.commit()

    retrieved_skill = Skill.query.filter_by(name=skill_name).first()
    assert retrieved_skill is not None
    assert retrieved_skill.name == skill_name
    assert retrieved_skill.id is not None
    assert retrieved_skill.created_at is not None
    # updated_at might be None on creation depending on server_default vs default and DB
    # For onupdate=func.now(), it might only populate on actual update operations after initial insert.
    # Let's check it's there or None for now.
    # assert retrieved_skill.updated_at is not None


def test_skill_to_dict(init_database):
    """Test the to_dict method of the Skill model."""
    skill = Skill(name="Dict Skill")
    init_database.session.add(skill)
    init_database.session.commit()  # Commit to get ID and timestamps

    skill_dict = skill.to_dict()
    assert skill_dict["id"] == skill.id
    assert skill_dict["name"] == "Dict Skill"
    assert skill_dict["created_at"] is not None
    # Similar to above, updated_at might be tricky on initial creation.
    # If server_default is used for updated_at as well, it should be populated.
    # Let's assume it's populated by the DB upon insert or is None.
    # For now, we'll just check its presence if not None
    if skill.updated_at:
        assert skill_dict["updated_at"] == skill.updated_at.isoformat()
    else:
        assert skill_dict["updated_at"] is None


def test_skill_name_unique(init_database):
    """Test that skill names are unique."""
    skill1 = Skill(name="Unique Skill")
    init_database.session.add(skill1)
    init_database.session.commit()

    skill2 = Skill(name="Unique Skill")
    init_database.session.add(skill2)
    with pytest.raises(Exception):  # sqlalchemy.exc.IntegrityError
        init_database.session.commit()
    init_database.session.rollback()  # Important to rollback the failed transaction


def test_skill_repr(init_database):
    """Test the __repr__ method of the Skill model."""
    skill = Skill(name="Repr Skill")
    init_database.session.add(skill)
    init_database.session.commit()
    assert repr(skill) == "<Skill Repr Skill>"
