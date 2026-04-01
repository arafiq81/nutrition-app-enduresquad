"""
Pytest configuration and shared fixtures.
"""
import pytest
from app import create_app, db as _db
from app.models import User
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create application configured for testing."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="session")
def db(app):
    return _db


@pytest.fixture(scope="function", autouse=True)
def clean_db(db):
    """Roll back all changes after each test."""
    yield
    db.session.rollback()
    # Truncate tables
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture
def athlete(db):
    """A fully-profiled athlete user for use in tests."""
    user = User(
        name="Test Athlete",
        email="test@example.com",
        age=35,
        sex="male",
        weight_kg=78.0,
        height_cm=180.0,
        body_fat_percentage=12.0,
        activity_level="moderate",
        training_phase="build",
        hr_max=185,
        hr_zone1_max=130,
        hr_zone2_max=148,
        hr_zone3_max=163,
        hr_zone4_max=175,
        profile_complete=True,
        approved=True,
    )
    user.set_password("testpassword123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def client(app):
    return app.test_client()
