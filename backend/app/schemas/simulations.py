"""Schemas for simulation endpoints"""
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Request to calculate simulation"""
    amount: float = Field(..., description="Requested loan amount", ge=0)
    term_months: int = Field(..., description="Requested term in months", ge=1, le=120)
    selected_account_id: str = Field(..., description="Selected disbursement account ID")


class SimulationResponse(BaseModel):
    """Simulation calculation result"""
    simulation_id: str = Field(..., description="Simulation identifier")
    offer_id: str = Field(..., description="Offer identifier")
    requested_amount: float = Field(..., description="Requested amount")
    requested_term_months: int = Field(..., description="Requested term")
    monthly_installment: float = Field(..., description="Calculated monthly payment")
    applied_tin: float = Field(..., description="Applied nominal interest rate (%)")
    applied_tae: float = Field(..., description="Applied APR (%)")
    total_cost: float = Field(..., description="Total repayment amount")
    total_interest: float = Field(..., description="Total interest to be paid")

    class Config:
        from_attributes = True


class SimulationConfirmRequest(BaseModel):
    """Confirm simulation and proceed to next step"""
    simulation_id: str = Field(..., description="Simulation identifier to confirm")
