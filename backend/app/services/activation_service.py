"""Activation Service - Loan activation and amortization schedule retrieval"""
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import AmortizationInstallment, AmortizationSchedule, LoanActivationProjection


class ActivationService:
    """
    Loan activation, amortization schedule retrieval, servicing handoff.
    Integrates with amortization schedule generator and active-loan servicing context.
    """

    def __init__(self, db: Session):
        self.db = db

    def activate_loan(
        self,
        journey_id: str,
        loan_id: str,
        customer_id: str,
        entity_id: str,
        amount: float,
        term_months: int,
        tin: float,
        installment_amount: float,
        first_due_date: datetime
    ) -> LoanActivationProjection:
        """
        Create loan activation projection.

        In production, waits for amortization schedule from generator
        and confirms servicing handoff.
        """
        servicing_reference = f"SVC_{uuid.uuid4().hex[:12].upper()}"

        projection = LoanActivationProjection(
            loan_id=loan_id,
            journey_id=journey_id,
            customer_id=customer_id,
            entity_id=entity_id,
            servicing_reference=servicing_reference,
            activation_status="ACTIVE"
        )

        self.db.add(projection)
        self.db.commit()
        self.db.refresh(projection)

        # Generate amortization schedule
        self._generate_amortization_schedule(
            loan_id=loan_id,
            amount=amount,
            term_months=term_months,
            tin=tin,
            installment_amount=installment_amount,
            first_due_date=first_due_date
        )

        return projection

    def _generate_amortization_schedule(
        self,
        loan_id: str,
        amount: float,
        term_months: int,
        tin: float,
        installment_amount: float,
        first_due_date: datetime
    ) -> AmortizationSchedule:
        """
        Generate amortization schedule.

        In production, calls amortization schedule generator adapter.
        """
        schedule_id = f"sch_{uuid.uuid4().hex[:16]}"

        # Create schedule header
        schedule = AmortizationSchedule(
            schedule_id=schedule_id,
            loan_id=loan_id,
            currency="EUR",
            installment_count=term_months
        )

        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)

        # Generate installments using French amortization
        self._generate_installments(
            schedule_id=schedule_id,
            loan_id=loan_id,
            principal=amount,
            term_months=term_months,
            monthly_rate=tin / 100 / 12,
            installment_amount=installment_amount,
            first_due_date=first_due_date
        )

        return schedule

    def _generate_installments(
        self,
        schedule_id: str,
        loan_id: str,
        principal: float,
        term_months: int,
        monthly_rate: float,
        installment_amount: float,
        first_due_date: datetime
    ) -> None:
        """Generate amortization installments"""
        outstanding_balance = principal

        for month in range(1, term_months + 1):
            # Calculate interest for this period
            interest_amount = outstanding_balance * monthly_rate

            # Calculate principal payment
            principal_amount = installment_amount - interest_amount

            # Update outstanding balance
            outstanding_balance -= principal_amount

            # Ensure last installment accounts for rounding
            if month == term_months:
                principal_amount += outstanding_balance
                outstanding_balance = 0

            # Calculate due date
            due_date = first_due_date + timedelta(days=30 * (month - 1))

            installment = AmortizationInstallment(
                schedule_id=schedule_id,
                loan_id=loan_id,
                installment_number=month,
                due_date=due_date,
                principal_amount=Decimal(str(round(principal_amount, 2))),
                interest_amount=Decimal(str(round(interest_amount, 2))),
                total_amount=Decimal(str(round(installment_amount, 2)))
            )

            self.db.add(installment)

        self.db.commit()

    def get_activation_status(
        self,
        journey_id: str
    ) -> Optional[LoanActivationProjection]:
        """Get loan activation projection for a journey"""
        return self.db.query(LoanActivationProjection).filter(
            LoanActivationProjection.journey_id == journey_id
        ).first()

    def get_amortization_schedule(
        self,
        loan_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get complete amortization schedule for a loan"""
        schedule = self.db.query(AmortizationSchedule).filter(
            AmortizationSchedule.loan_id == loan_id
        ).first()

        if not schedule:
            return None

        installments = self.db.query(AmortizationInstallment).filter(
            AmortizationInstallment.loan_id == loan_id
        ).order_by(
            AmortizationInstallment.installment_number
        ).all()

        return {
            "schedule_id": schedule.schedule_id,
            "loan_id": schedule.loan_id,
            "currency": schedule.currency,
            "installment_count": schedule.installment_count,
            "installments": [
                {
                    "installment_number": inst.installment_number,
                    "due_date": inst.due_date.isoformat(),
                    "principal_amount": float(inst.principal_amount),
                    "interest_amount": float(inst.interest_amount),
                    "total_amount": float(inst.total_amount)
                }
                for inst in installments
            ]
        }
