"""Unit tests for auth router - login endpoint"""
import pytest
from fastapi.testclient import TestClient

from app.auth import hash_password
from app.dependencies import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def client(db_session):
    """Create test client with db override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


def test_login_with_valid_credentials(db_session):
    """Test POST /api/v1/auth/login with valid credentials"""
    # Create test user
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "access_token" in data
    assert "token_type" in data
    assert "user" in data

    # Check token type
    assert data["token_type"] == "bearer"

    # Check user info
    user_data = data["user"]
    assert user_data["id"] == user.id
    assert user_data["username"] == "admin"
    assert user_data["email"] == "admin@example.com"
    assert user_data["entity_id"] == "ENTITY001"
    assert user_data["is_admin"] is True


def test_login_with_invalid_email(db_session):
    """Test login fails with non-existent email"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_with_invalid_password(db_session):
    """Test login fails with wrong password"""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("correctpassword"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Attempt login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_with_malformed_request():
    """Test login fails with malformed request"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "not-an-email",
            "password": "pass123"
        }
    )

    # Pydantic validation should fail for invalid email format
    assert response.status_code == 422


def test_login_token_can_be_used_for_authentication(db_session, client):
    """Test that login token can be used to access protected routes"""
    # Create test user
    user = User(
        username="authuser",
        email="auth@example.com",
        hashed_password=hash_password("testpass"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "auth@example.com",
            "password": "testpass"
        }
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Try to access a protected route with token
    # Use journey list endpoint as example (requires auth)
    protected_response = client.get(
        "/api/v1/journey/customer_123",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should not get 401 Unauthorized (may get 404 or other code, but not auth failure)
    assert protected_response.status_code != 401
