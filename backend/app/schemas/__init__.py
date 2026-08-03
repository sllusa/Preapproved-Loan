"""Pydantic schemas for request/response validation"""
from app.schemas.accounts import AccountResponse, AccountsListResponse
from app.schemas.activation import (
    AmortizationScheduleResponse,
    LoanActivationResponse,
)
from app.schemas.booking import BookingExecuteRequest, BookingStatusResponse
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.documents import (
    DocumentAcknowledgementRequest,
    DocumentPackageResponse,
)
from app.schemas.journey import JourneyResponse, JourneyResumeResponse
from app.schemas.offers import OfferResponse, OffersListResponse
from app.schemas.signature import (
    SignatureCallbackRequest,
    SignatureInitiateRequest,
    SignatureSessionResponse,
)
from app.schemas.simulations import (
    SimulationConfirmRequest,
    SimulationRequest,
    SimulationResponse,
)
from app.schemas.verifications import VerificationStatusResponse

__all__ = [
    "ErrorResponse",
    "PaginatedResponse",
    "OfferResponse",
    "OffersListResponse",
    "SimulationRequest",
    "SimulationResponse",
    "SimulationConfirmRequest",
    "AccountResponse",
    "AccountsListResponse",
    "DocumentPackageResponse",
    "DocumentAcknowledgementRequest",
    "VerificationStatusResponse",
    "SignatureInitiateRequest",
    "SignatureSessionResponse",
    "SignatureCallbackRequest",
    "BookingExecuteRequest",
    "BookingStatusResponse",
    "LoanActivationResponse",
    "AmortizationScheduleResponse",
    "JourneyResponse",
    "JourneyResumeResponse",
]
