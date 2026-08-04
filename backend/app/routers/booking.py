"""IRIS booking and disbursement routes"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.booking import BookingStatusResponse
from app.schemas.common import ErrorResponse
from app.services.booking_service import BookingService

router = APIRouter(tags=["booking"])


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/booking/execute",
    response_model=BookingStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
def execute_booking(
    journey_id: str,
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute idempotent IRIS booking and disbursement.

    Implements write-before-send idempotency pattern.
    """
    try:
        booking_service = BookingService(db)

        command = booking_service.execute_booking_and_disbursement(
            journey_id=journey_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"]
        )

        return BookingStatusResponse(
            booking_id=command.booking_id,
            journey_id=command.journey_id,
            iris_loan_id=command.iris_loan_id,
            booking_status=command.booking_status,
            disbursement_status=command.disbursement_status,
            executed_at=command.executed_at,
            reconciliation_case_id=None
        )

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


@router.get(
    "/api/v1/preapproved-loans/journeys/{journey_id}/booking/status",
    response_model=BookingStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Booking Not Found"}
    }
)
def get_booking_status(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poll booking and disbursement status.

    Returns current status and reconciliation case ID if uncertain.
    """
    try:
        booking_service = BookingService(db)

        # Get latest booking command for journey
        command = booking_service.get_booking_command_by_journey(journey_id)
        if not command:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Booking command not found", "status_code": 404, "retryable": False}
            )

        # Check for reconciliation case
        reconciliation_case_id = None
        if command.booking_status == "UNCERTAIN":
            from app.models import ReconciliationCase
            case = db.query(ReconciliationCase).filter(
                ReconciliationCase.booking_id == command.booking_id
            ).first()
            if case:
                reconciliation_case_id = case.case_id

        return BookingStatusResponse(
            booking_id=command.booking_id,
            journey_id=command.journey_id,
            iris_loan_id=command.iris_loan_id,
            booking_status=command.booking_status,
            disbursement_status=command.disbursement_status,
            executed_at=command.executed_at,
            reconciliation_case_id=reconciliation_case_id
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
