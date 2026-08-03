"""Authentication module with JWT and bcrypt"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password as string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password using bcrypt.

    Args:
        plain_password: Plain text password from user
        hashed_password: Stored hashed password

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(customer_id: str, entity_id: str, user_id: int) -> str:
    """
    Generate JWT access token with customer_id, entity_id, and exp claims.

    Args:
        customer_id: Customer identifier
        entity_id: Entity identifier
        user_id: User database ID

    Returns:
        Encoded JWT token string
    """
    expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "customer_id": customer_id,
        "entity_id": entity_id,
        "user_id": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload dict if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user by email and password.

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        db: Database session
        user_id: User database ID

    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()
