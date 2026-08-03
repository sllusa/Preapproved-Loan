"""Schemas for signature endpoints"""
from datetime import datetime

from pydantic import BaseModel, Field


class SignatureInitiateRequest(BaseModel):
    """Initiate PSD2/SCA signature session"""
    journey_id: str = Field(..., description="Journey identifier")
    callback_url: str = Field(..., description="Callback URL for signature completion")


class SignatureSessionResponse(BaseModel):
    """Signature session response"""
    session_id: str = Field(..., description="Signature session identifier")
    journey_id: str = Field(..., description="Journey identifier")
    provider_url: str = Field(..., description="SCA provider redirect URL")
    expires_at: datetime = Field(..., description="Session expiry timestamp")
    status: str = Field(..., description="Session status: INITIATED, COMPLETED, EXPIRED, CANCELLED")

    class Config:
        from_attributes = True


class SignatureCallbackRequest(BaseModel):
    """Signature callback from SCA provider"""
    session_id: str = Field(..., description="Signature session identifier")
    status: str = Field(..., description="Signature status: COMPLETED, CANCELLED, FAILED")
    signed_at: datetime | None = Field(None, description="Signature timestamp if completed")
    provider_reference: str | None = Field(None, description="Provider reference identifier")
