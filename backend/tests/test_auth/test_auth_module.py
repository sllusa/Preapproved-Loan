"""Unit tests for auth module - password hashing and JWT"""
from datetime import datetime, timedelta

import jwt

from app.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_user_by_id,
    hash_password,
    verify_password,
)
from app.config import settings
from app.models.user import User


def test_hash_password_returns_different_hash_each_time():
    """Test that bcrypt generates different hashes for same password"""
    password = "testpassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different hashes due to different salts
    assert hash1 != hash2
    # Both should be valid bcrypt hashes (start with $2b$)
    assert hash1.startswith("$2b$")
    assert hash2.startswith("$2b$")


def test_verify_password_with_correct_password():
    """Test password verification succeeds with correct password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_with_incorrect_password():
    """Test password verification fails with incorrect password"""
    password = "mySecurePassword123"
    hashed = hash_password(password)

    assert verify_password("wrongPassword", hashed) is False


def test_create_access_token_includes_required_claims():
    """Test JWT token includes customer_id, entity_id, user_id, and exp claims"""
    customer_id = "customer_123"
    entity_id = "ENTITY001"
    user_id = 42

    token = create_access_token(customer_id, entity_id, user_id)

    # Decode without verification to inspect claims
    payload = jwt.decode(token, options={"verify_signature": False})

    assert payload["customer_id"] == customer_id
    assert payload["entity_id"] == entity_id
    assert payload["user_id"] == str(user_id)
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_expiration():
    """Test JWT token expires after configured time"""
    token = create_access_token("customer_001", "ENTITY001", 1)

    payload = jwt.decode(token, options={"verify_signature": False})
    exp = datetime.fromtimestamp(payload["exp"])
    iat = datetime.fromtimestamp(payload["iat"])

    # Expiration should be approximately jwt_expiration_minutes from issue time
    delta = exp - iat
    expected_delta = timedelta(minutes=settings.jwt_expiration_minutes)

    # Allow 10 second variance for test execution time
    assert abs(delta.total_seconds() - expected_delta.total_seconds()) < 10


def test_decode_access_token_with_valid_token():
    """Test decoding valid JWT token returns payload"""
    customer_id = "customer_456"
    entity_id = "ENTITY002"
    user_id = 99

    token = create_access_token(customer_id, entity_id, user_id)
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["customer_id"] == customer_id
    assert payload["entity_id"] == entity_id
    assert payload["user_id"] == str(user_id)


def test_decode_access_token_with_invalid_token():
    """Test decoding invalid JWT token returns None"""
    invalid_token = "invalid.jwt.token"

    payload = decode_access_token(invalid_token)

    assert payload is None


def test_decode_access_token_with_expired_token():
    """Test decoding expired JWT token returns None"""
    # Create token with negative expiration (already expired)
    expire = datetime.utcnow() - timedelta(minutes=5)
    payload = {
        "customer_id": "customer_001",
        "entity_id": "ENTITY001",
        "user_id": "1",
        "exp": expire
    }
    expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    result = decode_access_token(expired_token)

    assert result is None


def test_authenticate_user_with_valid_credentials(db_session):
    """Test user authentication succeeds with valid email and password"""
    # Create test user
    password = "testpass123"
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password(password),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Authenticate
    result = authenticate_user(db_session, "test@example.com", password)

    assert result is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"


def test_authenticate_user_with_invalid_email(db_session):
    """Test user authentication fails with invalid email"""
    result = authenticate_user(db_session, "nonexistent@example.com", "anypassword")

    assert result is None


def test_authenticate_user_with_invalid_password(db_session):
    """Test user authentication fails with wrong password"""
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

    # Attempt with wrong password
    result = authenticate_user(db_session, "test@example.com", "wrongpassword")

    assert result is None


def test_authenticate_user_with_inactive_account(db_session):
    """Test user authentication fails for inactive account"""
    # Create inactive user
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        entity_id="ENTITY001",
        is_active=False,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Attempt authentication
    result = authenticate_user(db_session, "inactive@example.com", "password123")

    assert result is None


def test_get_user_by_id_returns_user(db_session):
    """Test retrieving user by ID"""
    # Create test user
    user = User(
        username="findme",
        email="findme@example.com",
        hashed_password=hash_password("pass123"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve by ID
    result = get_user_by_id(db_session, user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == "findme@example.com"


def test_get_user_by_id_returns_none_for_nonexistent(db_session):
    """Test retrieving non-existent user returns None"""
    result = get_user_by_id(db_session, 99999)

    assert result is None
