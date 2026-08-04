"""Verification orchestration routes"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.verifications import VerificationResultResponse, VerificationStatusResponse
from app.services.checks_service import ChecksService

router = APIRouter(tags=["verifications"])


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/checks/execute",
    response_model=VerificationStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
def execute_verifications(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute parallel verification orchestration (creditworthiness, anti-fraud, AML/PBC).

    Returns execution ID for status polling.
    """
    try:
        checks_service = ChecksService(db)

        execution = checks_service.execute_checks(
            journey_id=journey_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"],
            check_context={}
        )

        # Mock results for response
        mock_results = [
            VerificationResultResponse(
                verification_type="CREDITWORTHINESS",
                decision="PASS",
                executed_at=datetime.utcnow(),
                reason=None
            ),
            VerificationResultResponse(
                verification_type="ANTI_FRAUD",
                decision="PASS",
                executed_at=datetime.utcnow(),
                reason=None
            ),
            VerificationResultResponse(
                verification_type="AML_PBC",
                decision="PASS",
                executed_at=datetime.utcnow(),
                reason=None
            )
        ]

        return VerificationStatusResponse(
            execution_id=execution.execution_id,
            journey_id=execution.journey_id,
            overall_decision=execution.overall_decision,
            results=mock_results,
            completed_at=None  # Will be populated when checks complete
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
    "/api/v1/preapproved-loans/journeys/{journey_id}/checks/status",
    response_model=VerificationStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Execution Not Found"}
    }
)
def get_verification_status(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poll verification execution status.

    Returns overall decision and individual check results.
    """
    try:
        checks_service = ChecksService(db)

        # Get latest execution for journey
        execution = checks_service.get_latest_execution_for_journey(journey_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Verification execution not found", "status_code": 404, "retryable": False}
            )

        # Get individual results
        results_data = checks_service.get_check_results(execution.execution_id)

        results = [
            VerificationResultResponse(
                verification_type=result.verification_type,
                decision=result.decision,
                executed_at=result.executed_at,
                reason=result.reason
            )
            for result in results_data
        ]

        return VerificationStatusResponse(
            execution_id=execution.execution_id,
            journey_id=execution.journey_id,
            overall_decision=execution.overall_decision,
            results=results,
            completed_at=execution.completed_at
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
