"""Authentication router - login endpoint"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request payload"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User information in response"""
    id: int
    username: str
    email: str
    entity_id: str
    is_admin: bool


class LoginResponse(BaseModel):
    """Login response with access token and user info"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.

    POST /api/v1/auth/login

    Request body:
    {
        "email": "admin@example.com",
        "password": "admin123"
    }

    Response:
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "entity_id": "ENTITY001",
            "is_admin": true
        }
    }
    """
    user = authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token with customer_id, entity_id, exp claims
    # For this auth system, customer_id is the user's email
    access_token = create_access_token(
        customer_id=user.email,
        entity_id=user.entity_id,
        user_id=user.id
    )

    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            entity_id=user.entity_id,
            is_admin=user.is_admin
        )
    )
