"""Schemas for verification endpoints"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class VerificationResultResponse(BaseModel):
    """Individual verification result"""
    verification_type: str = Field(..., description="Verification type: CREDITWORTHINESS, ANTI_FRAUD, AML_PBC")
    decision: str = Field(..., description="Decision: PASS, REJECT, REVIEW")
    executed_at: datetime = Field(..., description="Execution timestamp")
    reason: str | None = Field(None, description="Decision reason if applicable")


class VerificationStatusResponse(BaseModel):
    """Verification orchestration status"""
    execution_id: str = Field(..., description="Execution identifier")
    journey_id: str = Field(..., description="Journey identifier")
    overall_decision: str = Field(..., description="Overall decision: PASS, REJECT, REVIEW")
    results: List[VerificationResultResponse] = Field(..., description="Individual verification results")
    completed_at: datetime | None = Field(None, description="Completion timestamp")

    class Config:
        from_attributes = True
