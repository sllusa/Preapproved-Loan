"""FastAPI dependencies for route handlers"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import decode_access_token, get_user_by_id
from app.database import SessionLocal

# HTTP Bearer token scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Authentication dependency for protected routes.

    Validates JWT token from Authorization header and returns user dict.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Dictionary with customer_id, entity_id, and user_id

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from payload
    user_id_str = payload.get("user_id")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user_id claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return dictionary with customer_id (email), entity_id, and user_id
    # for compatibility with all authenticated route handlers
    return {
        "customer_id": user.email,
        "entity_id": user.entity_id,
        "user_id": user.id
    }
