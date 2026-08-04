"""Schemas for loan activation and amortization endpoints"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class LoanActivationResponse(BaseModel):
    """Loan activation response"""
    activation_id: str = Field(..., description="Activation projection identifier")
    journey_id: str = Field(..., description="Journey identifier")
    iris_loan_id: str = Field(..., description="IRIS loan identifier")
    loan_status: str = Field(..., description="Loan status: ACTIVO")
    activation_timestamp: datetime = Field(..., description="Activation timestamp")
    first_due_date: datetime = Field(..., description="First installment due date")
    servicing_reference: str | None = Field(None, description="Servicing system reference")

    class Config:
        from_attributes = True


class AmortizationInstallmentResponse(BaseModel):
    """Individual amortization installment"""
    installment_number: int = Field(..., description="Installment number")
    due_date: datetime = Field(..., description="Due date")
    principal: float = Field(..., description="Principal portion")
    interest: float = Field(..., description="Interest portion")
    total_payment: float = Field(..., description="Total payment amount")
    remaining_balance: float = Field(..., description="Remaining balance after payment")


class AmortizationScheduleResponse(BaseModel):
    """Complete amortization schedule"""
    schedule_id: str = Field(..., description="Schedule identifier")
    journey_id: str = Field(..., description="Journey identifier")
    iris_loan_id: str = Field(..., description="IRIS loan identifier")
    installments: List[AmortizationInstallmentResponse] = Field(..., description="Installment schedule")
    total_installments: int = Field(..., description="Total number of installments")
    total_principal: float = Field(..., description="Total principal")
    total_interest: float = Field(..., description="Total interest")

    class Config:
        from_attributes = True
