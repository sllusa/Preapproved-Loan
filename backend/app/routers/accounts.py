"""Disbursement account selection routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.accounts import AccountResponse, AccountsListResponse
from app.schemas.common import ErrorResponse

router = APIRouter(tags=["accounts"])


@router.get(
    "/api/v1/preapproved-loans/journeys/{journey_id}/accounts",
    response_model=AccountsListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def list_disbursement_accounts(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve eligible disbursement accounts for the customer.

    Returns list of accounts with operability status and blocking reasons.
    In production, this would call the account validation adapter.
    """
    try:
        # Mock account data (in production: call account_adapter)
        mock_accounts = [
            {
                "account_id": "acc_001",
                "account_number": "****1234",
                "account_type": "CHECKING",
                "is_operable": True,
                "blocking_reason": None
            },
            {
                "account_id": "acc_002",
                "account_number": "****5678",
                "account_type": "SAVINGS",
                "is_operable": False,
                "blocking_reason": "ACCOUNT_BLOCKED"
            }
        ]

        accounts = [
            AccountResponse(**account)
            for account in mock_accounts
        ]

        return AccountsListResponse(accounts=accounts, total=len(accounts))

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/accounts/select",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Account not operable"}
    }
)
def select_disbursement_account(
    journey_id: str,
    request_body: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Select a disbursement account for the loan.

    Validates account operability and advances journey state.
    """
    try:
        from app.models import DisbursementAccountSelection
        from app.services.journey_orchestrator import JourneyOrchestrator

        # Extract account_id from request body
        account_id = request_body.get("account_id")
        if not account_id:
            raise ValueError("account_id is required")

        # Validate account operability (in production: call account_adapter)
        # For now, accept acc_001 as operable
        if account_id not in ["acc_001"]:
            raise ValueError("Account is not operable for disbursement")

        # Store account selection
        selection = DisbursementAccountSelection(
            journey_id=journey_id,
            account_id=account_id,
            account_number="****1234",
            account_type="CHECKING"
        )
        db.add(selection)
        db.commit()

        # Update journey reference
        journey_orchestrator = JourneyOrchestrator(db)
        _journey = journey_orchestrator.update_journey_reference(
            journey_id=journey_id,
            selected_account_id=account_id
        )

        # Advance state to next step
        _journey = journey_orchestrator.apply_transition(
            journey_id=journey_id,
            target_state="PENDIENTE_VERIFICACIONES",
            trigger="ACCOUNT_SELECTED",
            actor_type="CUSTOMER"
        )

        return {
            "journey_id": journey_id,
            "selected_account_id": account_id,
            "operable": True,
            "validated_at": selection.created_at.isoformat() if selection.created_at else None,
            "message": "Account selected, proceed to verifications"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": str(e), "status_code": 400, "retryable": False}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
