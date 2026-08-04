"""Loan activation and amortization schedule routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.activation import (
    AmortizationInstallmentResponse,
    AmortizationScheduleResponse,
    LoanActivationResponse,
)
from app.schemas.common import ErrorResponse

router = APIRouter(tags=["activation"])


@router.get(
    "/api/v1/preapproved-loans/journeys/{journey_id}/activation-status",
    response_model=LoanActivationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Activation Not Found"}
    }
)
def get_activation_status(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve loan activation status and details.

    Returns activation status, loan ID, servicing reference, and schedule metadata.
    """
    try:
        from app.models import LoanActivationProjection

        projection = db.query(LoanActivationProjection).filter(
            LoanActivationProjection.journey_id == journey_id
        ).first()

        if not projection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Loan activation not found", "status_code": 404, "retryable": False}
            )

        return LoanActivationResponse(
            activation_id=projection.activation_id,
            journey_id=projection.journey_id,
            iris_loan_id=projection.iris_loan_id,
            loan_status=projection.loan_status,
            activation_timestamp=projection.activation_timestamp,
            first_due_date=projection.first_due_date,
            servicing_reference=projection.servicing_reference
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )


@router.get(
    "/api/v1/preapproved-loans/loans/{loan_id}/amortization-schedule",
    response_model=AmortizationScheduleResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Schedule Not Found"}
    }
)
def get_amortization_schedule(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve complete amortization schedule for active loan.

    Returns full repayment schedule with principal, interest, and balance breakdown.
    """
    try:
        from app.models import AmortizationInstallment, AmortizationSchedule

        # Find schedule by IRIS loan ID
        schedule = db.query(AmortizationSchedule).filter(
            AmortizationSchedule.iris_loan_id == loan_id
        ).first()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Amortization schedule not found", "status_code": 404, "retryable": False}
            )

        # Get installments
        installments_data = db.query(AmortizationInstallment).filter(
            AmortizationInstallment.schedule_id == schedule.schedule_id
        ).order_by(AmortizationInstallment.installment_number).all()

        installments = [
            AmortizationInstallmentResponse(
                installment_number=inst.installment_number,
                due_date=inst.due_date,
                principal=inst.principal,
                interest=inst.interest,
                total_payment=inst.total_payment,
                remaining_balance=inst.remaining_balance
            )
            for inst in installments_data
        ]

        total_principal = sum(inst.principal for inst in installments_data)
        total_interest = sum(inst.interest for inst in installments_data)

        return AmortizationScheduleResponse(
            schedule_id=schedule.schedule_id,
            journey_id=schedule.journey_id,
            iris_loan_id=schedule.iris_loan_id,
            installments=installments,
            total_installments=len(installments),
            total_principal=total_principal,
            total_interest=total_interest
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
