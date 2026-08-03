"""Unit tests for auth dependencies - get_current_user"""
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import create_access_token, hash_password
from app.dependencies import get_current_user
from app.models.user import User


def test_get_current_user_with_valid_token(db_session):
    """Test get_current_user returns user dictionary with valid token"""
    # Create test user
    user = User(
        username="validuser",
        email="valid@example.com",
        hashed_password=hash_password("password"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Create valid token
    token = create_access_token("valid@example.com", "ENTITY001", user.id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    # Call dependency
    result = get_current_user(credentials, db_session)

    assert result is not None
    assert isinstance(result, dict)
    assert result["user_id"] == user.id
    assert result["customer_id"] == "valid@example.com"
    assert result["entity_id"] == "ENTITY001"


def test_get_current_user_with_invalid_token(db_session):
    """Test get_current_user raises 401 with invalid token"""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_with_nonexistent_user(db_session):
    """Test get_current_user raises 401 when user doesn't exist"""
    # Create token for non-existent user
    token = create_access_token("ghost@example.com", "ENTITY001", 99999)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail


def test_get_current_user_with_inactive_user(db_session):
    """Test get_current_user raises 401 for inactive user"""
    # Create inactive user
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=hash_password("password"),
        entity_id="ENTITY001",
        is_active=False,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Create token for inactive user
    token = create_access_token("inactive@example.com", "ENTITY001", user.id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert "inactive" in exc_info.value.detail.lower()


def test_get_current_user_with_token_missing_user_id(db_session):
    """Test get_current_user raises 401 when token missing user_id claim"""
    # Manually create token without user_id
    from datetime import datetime, timedelta

    import jwt

    from app.config import settings

    payload = {
        "customer_id": "customer_001",
        "entity_id": "ENTITY001",
        # Missing user_id
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert "missing user_id" in exc_info.value.detail.lower()


def test_get_current_user_with_malformed_user_id(db_session):
    """Test get_current_user raises 401 when user_id is not a valid integer"""
    # Manually create token with non-integer user_id
    from datetime import datetime, timedelta

    import jwt

    from app.config import settings

    payload = {
        "customer_id": "customer_001",
        "entity_id": "ENTITY001",
        "user_id": "not-an-integer",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials, db_session)

    assert exc_info.value.status_code == 401
    assert "Invalid user_id" in exc_info.value.detail
