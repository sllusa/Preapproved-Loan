"""Schemas for journey endpoints"""
from datetime import datetime

from pydantic import BaseModel, Field


class JourneyResponse(BaseModel):
    """Journey instance response"""
    journey_id: str = Field(..., description="Journey identifier")
    customer_id: str = Field(..., description="Customer identifier")
    entity_id: str = Field(..., description="Entity identifier")
    offer_id: str = Field(..., description="Offer identifier")
    current_state: str = Field(..., description="Current lifecycle state")
    channel_last_used: str = Field(..., description="Last used channel: APP, WEB")
    created_at: datetime = Field(..., description="Journey creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    resume_deadline_at: datetime | None = Field(None, description="Resume deadline timestamp")

    class Config:
        from_attributes = True


class JourneyResumeResponse(BaseModel):
    """Journey resume information"""
    journey: JourneyResponse = Field(..., description="Journey instance")
    can_resume: bool = Field(..., description="Whether journey can be resumed")
    next_step: str = Field(..., description="Next step in the journey")
    reason: str | None = Field(None, description="Reason if cannot resume")
