"""Booking Service - Idempotent IRIS booking and disbursement"""
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import BookingCommand, IdempotencyRecord, ReconciliationCase


class BookingService:
    """
    Implements idempotent command pattern with write-before-send idempotency records.
    Protects against duplicate disbursement through deterministic idempotency keys.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_idempotency_key(
        self,
        entity_id: str,
        journey_id: str,
        offer_id: str,
        signed_contract_digest: str,
        command_type: str = "BOOK",
        version: str = "v1"
    ) -> str:
        """
        Generate deterministic idempotency key.

        Format: {entityId}:{journeyId}:{offerId}:{digest}:{commandType}:{version}
        """
        key = f"{entity_id}:{journey_id}:{offer_id}:{signed_contract_digest}:{command_type}:{version}"
        return key

    def execute_booking(
        self,
        journey_id: str,
        entity_id: str,
        offer_id: str,
        customer_id: str,
        amount: float,
        term_months: int,
        disbursement_account_id: str,
        signed_contract_digest: str
    ) -> Dict[str, Any]:
        """
        Execute idempotent booking command to IRIS.

        Implements write-before-send pattern:
        1. Write idempotency record
        2. Call IRIS booking adapter
        3. Record booking command result
        4. If uncertain, create reconciliation case

        Returns:
            {
                "booking_command_id": str,
                "status": "CONFIRMED" | "PENDING_RECONCILIATION" | "FAILED",
                "iris_reference": optional IRIS reference,
                "requires_reconciliation": bool
            }
        """
        # Generate idempotency key
        idempotency_key = self.generate_idempotency_key(
            entity_id=entity_id,
            journey_id=journey_id,
            offer_id=offer_id,
            signed_contract_digest=signed_contract_digest
        )

        # Check if idempotency record exists
        existing_record = self.db.query(IdempotencyRecord).filter(
            IdempotencyRecord.idempotency_key == idempotency_key
        ).first()

        if existing_record:
            # Idempotent: return existing booking command
            booking_command = self.db.query(BookingCommand).filter(
                BookingCommand.idempotency_key == idempotency_key
            ).first()

            if booking_command:
                return {
                    "booking_command_id": booking_command.command_id,
                    "status": booking_command.status,
                    "iris_reference": booking_command.iris_reference,
                    "requires_reconciliation": booking_command.status == "PENDING_RECONCILIATION"
                }

        # Write idempotency record BEFORE external call
        idempotency_record = IdempotencyRecord(
            idempotency_key=idempotency_key,
            journey_id=journey_id,
            entity_id=entity_id,
            command_type="BOOK",
            status="PROCESSING"
        )

        try:
            self.db.add(idempotency_record)
            self.db.commit()
        except Exception:
            self.db.rollback()
            # Race condition: another request wrote the same key
            return self.execute_booking(
                journey_id=journey_id,
                entity_id=entity_id,
                offer_id=offer_id,
                customer_id=customer_id,
                amount=amount,
                term_months=term_months,
                disbursement_account_id=disbursement_account_id,
                signed_contract_digest=signed_contract_digest
            )

        # Call IRIS booking adapter
        # In production: iris_adapter.book_loan()
        # For now, simulate successful booking
        iris_result = self._simulate_iris_booking(
            journey_id=journey_id,
            amount=amount,
            term_months=term_months,
            account_id=disbursement_account_id
        )

        # Record booking command
        command_id = f"cmd_{uuid.uuid4().hex[:16]}"

        booking_command = BookingCommand(
            command_id=command_id,
            journey_id=journey_id,
            idempotency_key=idempotency_key,
            iris_reference=iris_result.get("iris_reference"),
            status=iris_result["status"],
            command_payload=iris_result.get("request_payload", {})
        )

        self.db.add(booking_command)

        # If uncertain response, create reconciliation case
        if iris_result["status"] == "PENDING_RECONCILIATION":
            reconciliation_case = ReconciliationCase(
                journey_id=journey_id,
                booking_command_id=command_id,
                status="PENDING",
                retry_count=0
            )
            self.db.add(reconciliation_case)

        # Update idempotency record status
        idempotency_record.status = iris_result["status"]

        self.db.commit()
        self.db.refresh(booking_command)

        return {
            "booking_command_id": command_id,
            "status": iris_result["status"],
            "iris_reference": iris_result.get("iris_reference"),
            "requires_reconciliation": iris_result["status"] == "PENDING_RECONCILIATION"
        }

    def _simulate_iris_booking(
        self,
        journey_id: str,
        amount: float,
        term_months: int,
        account_id: str
    ) -> Dict[str, Any]:
        """Simulate IRIS booking call (for testing)"""
        # Simulate successful booking
        return {
            "status": "CONFIRMED",
            "iris_reference": f"IRIS_{uuid.uuid4().hex[:12].upper()}",
            "request_payload": {
                "journey_id": journey_id,
                "amount": amount,
                "term_months": term_months,
                "account_id": account_id
            }
        }

    def get_booking_command_by_journey(
        self,
        journey_id: str
    ) -> Optional[BookingCommand]:
        """Get latest booking command for a journey"""
        return self.db.query(BookingCommand).filter(
            BookingCommand.journey_id == journey_id
        ).order_by(
            BookingCommand.created_at.desc()
        ).first()

    def get_booking_status(
        self,
        journey_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get latest booking status for a journey"""
        booking_command = self.get_booking_command_by_journey(journey_id)

        if not booking_command:
            return None

        return {
            "command_id": booking_command.command_id,
            "status": booking_command.status,
            "iris_reference": booking_command.iris_reference,
            "created_at": booking_command.created_at.isoformat(),
            "requires_reconciliation": booking_command.status == "PENDING_RECONCILIATION"
        }

    def get_reconciliation_case(
        self,
        journey_id: str
    ) -> Optional[ReconciliationCase]:
        """Get pending reconciliation case for a journey"""
        return self.db.query(ReconciliationCase).filter(
            ReconciliationCase.journey_id == journey_id,
            ReconciliationCase.status == "PENDING"
        ).first()
