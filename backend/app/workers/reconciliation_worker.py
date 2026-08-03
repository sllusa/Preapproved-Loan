"""Reconciliation Worker - Background polling for pending IRIS booking cases"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.iris_adapter import IRISAdapter
from app.database import SessionLocal
from app.models import BookingCommand, ReconciliationCase
from app.services.audit_service import AuditService
from app.services.journey_orchestrator import JourneyOrchestrator

logger = logging.getLogger(__name__)


class ReconciliationWorker:
    """
    Background worker for reconciling pending IRIS booking cases.

    Implements:
    - Periodic polling of pending reconciliation cases
    - Exponential backoff for retries
    - State advancement on confirmed resolution
    - Operator escalation after max retries
    - Audit event emission for all outcomes
    """

    def __init__(
        self,
        poll_interval_seconds: int = 30,
        max_retries: int = 10,
        initial_backoff_seconds: int = 2,
        max_backoff_seconds: int = 300
    ):
        """
        Initialize reconciliation worker.

        Args:
            poll_interval_seconds: Base polling interval between worker cycles
            max_retries: Maximum retry attempts before escalation
            initial_backoff_seconds: Initial exponential backoff delay
            max_backoff_seconds: Maximum exponential backoff delay
        """
        self.poll_interval = poll_interval_seconds
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff_seconds
        self.max_backoff = max_backoff_seconds
        self.iris_adapter = IRISAdapter()
        self.running = False

    async def start(self):
        """Start the reconciliation worker background task"""
        self.running = True
        logger.info("Reconciliation worker started")

        while self.running:
            try:
                await self._process_pending_cases()
            except Exception as e:
                logger.error(f"Error in reconciliation worker cycle: {str(e)}")

            # Wait before next cycle
            await asyncio.sleep(self.poll_interval)

    async def stop(self):
        """Stop the reconciliation worker"""
        self.running = False
        logger.info("Reconciliation worker stopped")

    async def _process_pending_cases(self):
        """Process all pending reconciliation cases"""
        db = SessionLocal()
        try:
            # Query pending cases
            pending_cases = db.query(ReconciliationCase).filter(
                ReconciliationCase.status == "PENDING"
            ).all()

            if not pending_cases:
                logger.debug("No pending reconciliation cases")
                return

            logger.info(f"Processing {len(pending_cases)} pending reconciliation cases")

            for case in pending_cases:
                try:
                    await self._process_single_case(db, case)
                except Exception as e:
                    logger.error(
                        f"Error processing case {case.reconciliation_case_id}: {str(e)}"
                    )
                    # Continue with next case rather than failing entire batch
                    continue

            db.commit()

        except Exception as e:
            logger.error(f"Error querying pending cases: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def _process_single_case(
        self,
        db: Session,
        case: ReconciliationCase
    ):
        """
        Process a single reconciliation case.

        Args:
            db: Database session
            case: Reconciliation case to process
        """
        # Check if we should retry based on exponential backoff
        if not self._should_retry(case):
            logger.debug(f"Skipping case {case.reconciliation_case_id} - backoff not expired")
            return

        # Get booking command
        booking_command = db.query(BookingCommand).filter(
            BookingCommand.booking_command_id == case.booking_command_id
        ).first()

        if not booking_command:
            logger.error(f"Booking command not found for case {case.reconciliation_case_id}")
            return

        # Check if max retries exceeded
        if case.retry_count >= self.max_retries:
            await self._escalate_to_operator(db, case, booking_command)
            return

        # Poll IRIS status
        try:
            # Extract IRIS reference from provider_payload
            provider_payload = booking_command.provider_payload or {}
            iris_reference = provider_payload.get("iris_reference")

            if not iris_reference:
                logger.warning(
                    f"No IRIS reference for booking {booking_command.booking_command_id} - "
                    f"cannot poll status"
                )
                case.retry_count += 1
                case.last_polled_at = datetime.utcnow()
                return

            logger.info(
                f"Polling IRIS status for case {case.reconciliation_case_id}, "
                f"IRIS reference {iris_reference}, attempt {case.retry_count + 1}"
            )

            # Call IRIS adapter with 2s timeout
            status_result = self.iris_adapter.get_booking_status(
                iris_reference=iris_reference,
                correlation_id=case.journey_id
            )

            # Update retry count and poll timestamp
            case.retry_count += 1
            case.last_polled_at = datetime.utcnow()

            # Handle confirmed success
            if status_result["status"] == "CONFIRMED":
                await self._handle_confirmed_success(db, case, booking_command, status_result)
                return

            # Handle confirmed failure
            if status_result["status"] == "FAILED":
                await self._handle_confirmed_failure(db, case, booking_command, status_result)
                return

            # Handle still pending
            if status_result["status"] in ("PENDING", "UNKNOWN"):
                logger.info(
                    f"Case {case.reconciliation_case_id} still pending, "
                    f"retry {case.retry_count}/{self.max_retries}"
                )
                # Continue retrying
                return

        except TimeoutError as e:
            logger.warning(
                f"Timeout polling IRIS for case {case.reconciliation_case_id}: {str(e)}"
            )
            case.retry_count += 1
            case.last_polled_at = datetime.utcnow()
            # Continue retrying

        except ValueError as e:
            logger.error(
                f"Error polling IRIS for case {case.reconciliation_case_id}: {str(e)}"
            )
            case.retry_count += 1
            case.last_polled_at = datetime.utcnow()
            # Continue retrying

    async def _handle_confirmed_success(
        self,
        db: Session,
        case: ReconciliationCase,
        booking_command: BookingCommand,
        status_result: dict
    ):
        """
        Handle confirmed IRIS booking success.

        Updates journey state to ABONADO, emits audit event, closes reconciliation case.
        """
        logger.info(
            f"IRIS booking confirmed for case {case.reconciliation_case_id}, "
            f"advancing to ABONADO"
        )

        # Update booking command status
        booking_command.booking_status = "CONFIRMED"
        booking_command.provider_status = "CONFIRMED"
        booking_command.pending_reconciliation = False
        booking_command.resolved_at = datetime.utcnow()

        # Close reconciliation case
        case.status = "RESOLVED_SUCCESS"

        # Advance journey state to ABONADO
        orchestrator = JourneyOrchestrator(db)
        audit_service = AuditService(db)

        try:
            journey = orchestrator.get_journey(case.journey_id)
            if journey:
                # Only transition if not already in a later state
                if journey.current_state in ("FIRMADO", "ABONADO"):
                    if journey.current_state == "FIRMADO":
                        provider_payload = booking_command.provider_payload or {}
                        iris_reference = provider_payload.get("iris_reference")
                        orchestrator.apply_transition(
                            journey_id=case.journey_id,
                            target_state="ABONADO",
                            trigger="RECONCILIATION_CONFIRMED",
                            actor_type="SYSTEM",
                            context={
                                "reconciliation_case_id": case.reconciliation_case_id,
                                "iris_reference": iris_reference,
                                "resolution": "CONFIRMED_BY_RECONCILIATION_WORKER"
                            }
                        )
                else:
                    logger.warning(
                        f"Journey {case.journey_id} in unexpected state "
                        f"{journey.current_state} for reconciliation success"
                    )

            # Emit audit event for reconciliation resolution
            provider_payload = booking_command.provider_payload or {}
            iris_reference = provider_payload.get("iris_reference")
            audit_service.emit_event(
                journey_id=case.journey_id,
                customer_id=journey.customer_id if journey else "UNKNOWN",
                entity_id=journey.entity_id if journey else "UNKNOWN",
                event_type="RECONCILIATION_RESOLVED",
                actor_type="SYSTEM",
                payload={
                    "reconciliation_case_id": case.reconciliation_case_id,
                    "booking_command_id": booking_command.booking_command_id,
                    "iris_reference": iris_reference,
                    "resolution": "SUCCESS",
                    "retry_count": case.retry_count,
                    "status_result": status_result
                },
                correlation_id=case.journey_id
            )

        except Exception as e:
            logger.error(
                f"Error advancing journey for case {case.reconciliation_case_id}: {str(e)}"
            )
            # Case is still marked resolved, but journey transition failed
            # This should be picked up by monitoring

    async def _handle_confirmed_failure(
        self,
        db: Session,
        case: ReconciliationCase,
        booking_command: BookingCommand,
        status_result: dict
    ):
        """
        Handle confirmed IRIS booking failure.

        Transitions to terminal failure state, emits audit event, generates operator task.
        """
        logger.info(
            f"IRIS booking failed for case {case.reconciliation_case_id}, "
            f"transitioning to terminal failure"
        )

        # Update booking command status
        booking_command.booking_status = "FAILED"
        booking_command.provider_status = "FAILED"
        booking_command.pending_reconciliation = False
        booking_command.resolved_at = datetime.utcnow()

        # Close reconciliation case
        case.status = "RESOLVED_FAILURE"

        # Generate support reference for operator
        support_ref = f"IRIS_FAIL_{uuid.uuid4().hex[:8].upper()}"
        case.support_reference = support_ref

        # Transition journey to CANCELADO (terminal failure after signed)
        orchestrator = JourneyOrchestrator(db)
        audit_service = AuditService(db)

        try:
            journey = orchestrator.get_journey(case.journey_id)
            if journey:
                # Only transition if not already terminal
                if not orchestrator.is_terminal_state(journey.current_state):
                    provider_payload = booking_command.provider_payload or {}
                    iris_reference = provider_payload.get("iris_reference")
                    orchestrator.apply_transition(
                        journey_id=case.journey_id,
                        target_state="CANCELADO",
                        trigger="RECONCILIATION_FAILED",
                        actor_type="SYSTEM",
                        context={
                            "reconciliation_case_id": case.reconciliation_case_id,
                            "iris_reference": iris_reference,
                            "support_reference": support_ref,
                            "resolution": "FAILED_BY_RECONCILIATION_WORKER"
                        }
                    )

            # Emit audit event for reconciliation failure
            provider_payload = booking_command.provider_payload or {}
            iris_reference = provider_payload.get("iris_reference")
            audit_service.emit_event(
                journey_id=case.journey_id,
                customer_id=journey.customer_id if journey else "UNKNOWN",
                entity_id=journey.entity_id if journey else "UNKNOWN",
                event_type="RECONCILIATION_RESOLVED",
                actor_type="SYSTEM",
                payload={
                    "reconciliation_case_id": case.reconciliation_case_id,
                    "booking_command_id": booking_command.booking_command_id,
                    "iris_reference": iris_reference,
                    "resolution": "FAILURE",
                    "support_reference": support_ref,
                    "retry_count": case.retry_count,
                    "status_result": status_result
                },
                correlation_id=case.journey_id
            )

            # Generate operator task record (in production: queue operator task)
            logger.info(
                f"Generated operator task for failed booking, support ref: {support_ref}"
            )

        except Exception as e:
            logger.error(
                f"Error transitioning journey for failed case {case.reconciliation_case_id}: {str(e)}"
            )

    async def _escalate_to_operator(
        self,
        db: Session,
        case: ReconciliationCase,
        booking_command: BookingCommand
    ):
        """
        Escalate case to operator after max retries exceeded.

        Marks case as escalated, generates support reference, emits audit event.
        """
        logger.warning(
            f"Max retries ({self.max_retries}) exceeded for case {case.reconciliation_case_id}, "
            f"escalating to operator"
        )

        # Generate support reference
        support_ref = f"IRIS_TIMEOUT_{uuid.uuid4().hex[:8].upper()}"

        # Update case status
        case.status = "ESCALATED_TO_OPERATOR"
        case.operator_assigned_at = datetime.utcnow()
        case.support_reference = support_ref

        # Update booking command
        booking_command.booking_status = "PENDING_MANUAL_REVIEW"
        booking_command.provider_status = "PENDING_MANUAL_REVIEW"

        # Emit audit event
        audit_service = AuditService(db)
        orchestrator = JourneyOrchestrator(db)

        try:
            journey = orchestrator.get_journey(case.journey_id)
            provider_payload = booking_command.provider_payload or {}
            iris_reference = provider_payload.get("iris_reference")

            audit_service.emit_event(
                journey_id=case.journey_id,
                customer_id=journey.customer_id if journey else "UNKNOWN",
                entity_id=journey.entity_id if journey else "UNKNOWN",
                event_type="RECONCILIATION_ESCALATED",
                actor_type="SYSTEM",
                payload={
                    "reconciliation_case_id": case.reconciliation_case_id,
                    "booking_command_id": booking_command.booking_command_id,
                    "iris_reference": iris_reference,
                    "support_reference": support_ref,
                    "retry_count": case.retry_count,
                    "reason": "MAX_RETRIES_EXCEEDED"
                },
                correlation_id=case.journey_id
            )

            # Generate operator task record (in production: create operator task in task system)
            logger.info(
                f"Escalated to operator with support reference: {support_ref}"
            )

        except Exception as e:
            logger.error(
                f"Error emitting escalation event for case {case.reconciliation_case_id}: {str(e)}"
            )

    def _should_retry(self, case: ReconciliationCase) -> bool:
        """
        Check if case should be retried based on exponential backoff.

        Args:
            case: Reconciliation case

        Returns:
            True if backoff period has elapsed, False otherwise
        """
        if case.last_polled_at is None:
            # Never polled, retry immediately
            return True

        # Calculate exponential backoff
        backoff_seconds = min(
            self.initial_backoff * (2 ** case.retry_count),
            self.max_backoff
        )

        # Check if enough time has elapsed
        next_retry_at = case.last_polled_at + timedelta(seconds=backoff_seconds)
        return datetime.utcnow() >= next_retry_at


# Global worker instance
_worker_instance: Optional[ReconciliationWorker] = None


async def start_reconciliation_worker(
    poll_interval_seconds: int = 30,
    max_retries: int = 10
):
    """Start the global reconciliation worker instance"""
    global _worker_instance

    if _worker_instance is not None:
        logger.warning("Reconciliation worker already running")
        return

    _worker_instance = ReconciliationWorker(
        poll_interval_seconds=poll_interval_seconds,
        max_retries=max_retries
    )

    await _worker_instance.start()


async def stop_reconciliation_worker():
    """Stop the global reconciliation worker instance"""
    global _worker_instance

    if _worker_instance is None:
        logger.warning("No reconciliation worker running")
        return

    await _worker_instance.stop()
    _worker_instance = None
