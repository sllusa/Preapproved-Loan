"""Pytest fixtures for router tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 - Import to register all models with Base
from app.database import Base
from app.dependencies import get_current_user, get_db
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # noqa: N806


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with dependency overrides"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_current_user():
        return {
            "customer_id": "test_customer_001",
            "entity_id": "test_entity_001",
            "user_id": 1
        }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {
        "customer_id": "test_customer_001",
        "entity_id": "test_entity_001",
        "user_id": 1
    }


@pytest.fixture
def mock_entity_config(test_db):
    """Create mock entity configuration"""
    from app.models import EntityConfiguration

    entity = EntityConfiguration(
        entity_id="test_entity_001",
        brand_code="TEST",
        is_active=True,
        min_amount=1000.0,
        max_term_months=60,
        legal_package_mode="SECCI",
        supported_languages=["es"],
        rollout_flags={},
        config_version="v1"
    )
    test_db.add(entity)
    test_db.commit()
    test_db.refresh(entity)
    return entity
