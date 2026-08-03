"""Schemas for booking and disbursement endpoints"""
from datetime import datetime

from pydantic import BaseModel, Field


class BookingExecuteRequest(BaseModel):
    """Execute IRIS booking and disbursement"""
    journey_id: str = Field(..., description="Journey identifier")


class BookingStatusResponse(BaseModel):
    """Booking and disbursement status"""
    booking_id: str = Field(..., description="Booking command identifier")
    journey_id: str = Field(..., description="Journey identifier")
    iris_loan_id: str | None = Field(None, description="IRIS loan identifier if booked")
    booking_status: str = Field(..., description="Booking status: CONFIRMED, PENDING, FAILED, UNCERTAIN")
    disbursement_status: str | None = Field(None, description="Disbursement status if applicable")
    executed_at: datetime = Field(..., description="Execution timestamp")
    reconciliation_case_id: str | None = Field(None, description="Reconciliation case ID if uncertain")

    class Config:
        from_attributes = True
