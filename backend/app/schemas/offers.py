"""Schemas for offer endpoints"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class OfferResponse(BaseModel):
    """Pre-approved offer response"""
    offer_id: str = Field(..., description="Unique offer identifier")
    customer_id: str = Field(..., description="Customer identifier")
    entity_id: str = Field(..., description="Banking entity identifier")
    max_amount: float = Field(..., description="Maximum loan amount", ge=0)
    max_term_months: int = Field(..., description="Maximum repayment term in months", ge=1, le=120)
    indicative_tin: float = Field(..., description="Indicative nominal interest rate (%)", ge=0, le=100)
    indicative_tae: float = Field(..., description="Indicative APR (%)", ge=0, le=100)
    validity_ends_at: datetime = Field(..., description="Offer expiry timestamp")
    offer_status: str = Field(..., description="Offer status: ACTIONABLE, NON_ACTIONABLE, EXPIRED, REVOKED")
    reason: str | None = Field(None, description="Non-actionable reason if applicable")

    class Config:
        from_attributes = True


class OffersListResponse(BaseModel):
    """List of offers for a customer"""
    offers: List[OfferResponse] = Field(..., description="Available offers")
    total: int = Field(..., description="Total number of offers")
