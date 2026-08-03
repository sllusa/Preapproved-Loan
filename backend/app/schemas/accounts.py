"""Schemas for disbursement account endpoints"""
from typing import List

from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """Disbursement account response"""
    account_id: str = Field(..., description="Account identifier")
    account_number: str = Field(..., description="Masked account number")
    account_type: str = Field(..., description="Account type")
    is_operable: bool = Field(..., description="Whether account is operable for disbursement")
    blocking_reason: str | None = Field(None, description="Reason if not operable")


class AccountsListResponse(BaseModel):
    """List of disbursement accounts"""
    accounts: List[AccountResponse] = Field(..., description="Customer accounts")
    total: int = Field(..., description="Total number of accounts")
