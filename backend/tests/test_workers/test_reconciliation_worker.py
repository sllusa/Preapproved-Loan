"""Tests for Reconciliation Worker"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    AuditEvent,
    BookingCommand,
    EntityConfiguration,
    JourneyInstance,
    ReconciliationCase,
)
from app.workers.reconciliation_worker import ReconciliationWorker


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)  # noqa: N806
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_entity(db_session):
    """Create sample entity configuration"""
    entity = EntityConfiguration(
        entity_id="ENTITY_001",
        brand_code="TEST_BRAND",
        is_active=True,
        min_amount=1000.0,
        max_term_months=60,
        legal_package_mode="SECCI",
        supported_languages=["es"],
        rollout_flags={},
        config_version="1.0",
    )
    db_session.add(entity)
    db_session.commit()
    return entity


@pytest.fixture
def sample_journey(db_session, sample_entity):
    """Create sample journey instance"""
    journey = JourneyInstance(
        journey_id=f"journey_{uuid.uuid4().hex[:12]}",
        customer_id="CUST_001",
        entity_id=sample_entity.entity_id,
        offer_id="OFFER_001",
        current_state="FIRMADO",
        channel_last_used="WEB",
        version=0,
    )
    db_session.add(journey)
    db_session.commit()
    return journey


@pytest.fixture
def sample_booking_command(db_session, sample_journey):
    """Create sample booking command"""
    iris_ref = f"IRIS_{uuid.uuid4().hex[:12].upper()}"
    command = BookingCommand(
        booking_command_id=f"cmd_{uuid.uuid4().hex[:16]}",
        journey_id=sample_journey.journey_id,
        idempotency_key=f"key_{uuid.uuid4().hex}",
        provider_status="PENDING",
        booking_status="PENDING_RECONCILIATION",
        pending_reconciliation=True,
        provider_payload={"iris_reference": iris_ref},
    )
    db_session.add(command)
    db_session.commit()
    return command


@pytest.fixture
def pending_reconciliation_case(db_session, sample_journey, sample_booking_command):
    """Create pending reconciliation case"""
    case = ReconciliationCase(
        reconciliation_case_id=f"recon_{uuid.uuid4().hex[:16]}",
        journey_id=sample_journey.journey_id,
        booking_command_id=sample_booking_command.booking_command_id,
        status="PENDING",
        retry_count=0,
    )
    db_session.add(case)
    db_session.commit()
    return case


@pytest.mark.asyncio
async def test_worker_queries_pending_cases(db_session, pending_reconciliation_case):
    """Test worker queries reconciliation_case table with status=PENDING"""
    worker = ReconciliationWorker(poll_interval_seconds=1, max_retries=10)
    case_id = pending_reconciliation_case.reconciliation_case_id

    # Mock SessionLocal to return our test session
    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        # Mock IRIS adapter to prevent actual HTTP calls
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            mock_status.return_value = {
                "status": "PENDING",
                "iris_reference": pending_reconciliation_case.booking_command_id,
            }

            # Run one processing cycle
            await worker._process_pending_cases()

            # Verify the case was queried and processed
            assert mock_status.called
            # Refresh the case from the database
            db_session.expire_all()
            case = db_session.query(ReconciliationCase).filter(
                ReconciliationCase.reconciliation_case_id == case_id
            ).first()
            assert case.retry_count == 1


@pytest.mark.asyncio
async def test_worker_polls_iris_with_timeout_and_backoff(
    db_session, pending_reconciliation_case, sample_booking_command
):
    """Test worker polls IRIS status API with 2s timeout and exponential backoff"""
    worker = ReconciliationWorker(
        poll_interval_seconds=1, max_retries=10, initial_backoff_seconds=2
    )

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            iris_ref = sample_booking_command.provider_payload.get("iris_reference")
            mock_status.return_value = {
                "status": "PENDING",
                "iris_reference": iris_ref,
            }

            # First poll
            await worker._process_single_case(db_session, pending_reconciliation_case)
            assert pending_reconciliation_case.retry_count == 1
            assert pending_reconciliation_case.last_polled_at is not None

            # Immediate second poll should be skipped due to backoff
            _first_poll_time = pending_reconciliation_case.last_polled_at
            should_retry = worker._should_retry(pending_reconciliation_case)
            assert not should_retry  # Backoff not expired

            # Simulate time passing beyond backoff (2^1 = 2 seconds minimum)
            pending_reconciliation_case.last_polled_at = datetime.utcnow() - timedelta(
                seconds=5
            )
            should_retry = worker._should_retry(pending_reconciliation_case)
            assert should_retry  # Backoff expired


@pytest.mark.asyncio
async def test_worker_handles_confirmed_success(
    db_session, pending_reconciliation_case, sample_booking_command, sample_journey
):
    """Test worker updates journey to ABONADO and closes case on confirmed success"""
    worker = ReconciliationWorker(poll_interval_seconds=1, max_retries=10)

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            iris_ref = sample_booking_command.provider_payload.get("iris_reference")
            mock_status.return_value = {
                "status": "CONFIRMED",
                "iris_reference": iris_ref,
            }

            # Process the case
            await worker._process_single_case(db_session, pending_reconciliation_case)

            # Verify booking command updated
            db_session.refresh(sample_booking_command)
            assert sample_booking_command.booking_status == "CONFIRMED"

            # Verify reconciliation case closed
            db_session.refresh(pending_reconciliation_case)
            assert pending_reconciliation_case.status == "RESOLVED_SUCCESS"

            # Verify journey transitioned to ABONADO
            db_session.refresh(sample_journey)
            assert sample_journey.current_state == "ABONADO"

            # Verify audit event emitted
            audit_events = db_session.query(AuditEvent).filter(
                AuditEvent.event_type == "RECONCILIATION_RESOLVED"
            ).all()
            assert len(audit_events) > 0


@pytest.mark.asyncio
async def test_worker_handles_confirmed_failure(
    db_session, pending_reconciliation_case, sample_booking_command, sample_journey
):
    """Test worker transitions to terminal failure and generates operator task on failure"""
    worker = ReconciliationWorker(poll_interval_seconds=1, max_retries=10)

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            iris_ref = sample_booking_command.provider_payload.get("iris_reference")
            mock_status.return_value = {
                "status": "FAILED",
                "iris_reference": iris_ref,
                "message": "IRIS booking rejected",
            }

            # Process the case
            await worker._process_single_case(db_session, pending_reconciliation_case)

            # Verify booking command updated
            db_session.refresh(sample_booking_command)
            assert sample_booking_command.booking_status == "FAILED"

            # Verify reconciliation case closed
            db_session.refresh(pending_reconciliation_case)
            assert pending_reconciliation_case.status == "RESOLVED_FAILURE"
            assert pending_reconciliation_case.support_reference is not None
            assert pending_reconciliation_case.support_reference.startswith("IRIS_FAIL_")

            # Verify journey transitioned to CANCELADO
            db_session.refresh(sample_journey)
            assert sample_journey.current_state == "CANCELADO"

            # Verify audit event emitted
            audit_events = db_session.query(AuditEvent).filter(
                AuditEvent.event_type == "RECONCILIATION_RESOLVED"
            ).all()
            assert len(audit_events) > 0


@pytest.mark.asyncio
async def test_worker_escalates_after_max_retries(
    db_session, pending_reconciliation_case, sample_booking_command
):
    """Test worker escalates to operator after max retries with support reference"""
    worker = ReconciliationWorker(
        poll_interval_seconds=1, max_retries=3, initial_backoff_seconds=0
    )

    # Set retry count to max
    pending_reconciliation_case.retry_count = 3
    db_session.commit()

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            iris_ref = sample_booking_command.provider_payload.get("iris_reference")
            mock_status.return_value = {
                "status": "PENDING",
                "iris_reference": iris_ref,
            }

            # Process the case
            await worker._process_single_case(db_session, pending_reconciliation_case)

            # Verify case escalated
            db_session.refresh(pending_reconciliation_case)
            assert pending_reconciliation_case.status == "ESCALATED_TO_OPERATOR"
            assert pending_reconciliation_case.operator_assigned_at is not None
            assert pending_reconciliation_case.support_reference is not None
            assert pending_reconciliation_case.support_reference.startswith(
                "IRIS_TIMEOUT_"
            )

            # Verify booking command updated
            db_session.refresh(sample_booking_command)
            assert sample_booking_command.booking_status == "PENDING_MANUAL_REVIEW"

            # Verify audit event emitted
            audit_events = db_session.query(AuditEvent).filter(
                AuditEvent.event_type == "RECONCILIATION_ESCALATED"
            ).all()
            assert len(audit_events) > 0


@pytest.mark.asyncio
async def test_worker_handles_timeout_error(
    db_session, pending_reconciliation_case, sample_booking_command
):
    """Test worker handles IRIS timeout and continues retrying"""
    worker = ReconciliationWorker(poll_interval_seconds=1, max_retries=10)
    case_id = pending_reconciliation_case.reconciliation_case_id

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            # Simulate timeout
            mock_status.side_effect = TimeoutError("IRIS timeout")

            # Process the case
            await worker._process_single_case(db_session, pending_reconciliation_case)

            # Commit changes made during processing
            db_session.commit()

            # Refresh from database
            db_session.expire_all()
            case = db_session.query(ReconciliationCase).filter(
                ReconciliationCase.reconciliation_case_id == case_id
            ).first()

            # Verify retry count incremented
            assert case.retry_count == 1
            assert case.last_polled_at is not None
            # Case should still be PENDING (not escalated yet)
            assert case.status == "PENDING"


@pytest.mark.asyncio
async def test_worker_exponential_backoff_calculation():
    """Test exponential backoff delay increases correctly"""
    worker = ReconciliationWorker(
        poll_interval_seconds=1,
        max_retries=10,
        initial_backoff_seconds=2,
        max_backoff_seconds=60,
    )

    # Create mock case with different retry counts
    case_0 = ReconciliationCase(
        reconciliation_case_id="recon_1",
        journey_id="journey_1",
        booking_command_id="cmd_1",
        status="PENDING",
        retry_count=0,
        last_polled_at=datetime.utcnow() - timedelta(seconds=3),
    )

    case_3 = ReconciliationCase(
        reconciliation_case_id="recon_2",
        journey_id="journey_2",
        booking_command_id="cmd_2",
        status="PENDING",
        retry_count=3,
        last_polled_at=datetime.utcnow() - timedelta(seconds=10),
    )

    case_10 = ReconciliationCase(
        reconciliation_case_id="recon_3",
        journey_id="journey_3",
        booking_command_id="cmd_3",
        status="PENDING",
        retry_count=10,
        last_polled_at=datetime.utcnow() - timedelta(seconds=70),
    )

    # Verify backoff increases: 2, 4, 8, 16, 32, 64 (capped at max_backoff=60)
    # retry_count=0: 2 * (2^0) = 2 seconds
    assert worker._should_retry(case_0)

    # retry_count=3: 2 * (2^3) = 16 seconds, last polled 10 seconds ago -> not ready
    assert not worker._should_retry(case_3)

    # retry_count=10: 2 * (2^10) = 2048 -> capped at 60, last polled 70 seconds ago -> ready
    assert worker._should_retry(case_10)


@pytest.mark.asyncio
async def test_worker_emits_audit_events(
    db_session, pending_reconciliation_case, sample_booking_command, sample_journey
):
    """Test worker emits audit events for all outcomes"""
    worker = ReconciliationWorker(poll_interval_seconds=1, max_retries=10)

    with patch("app.workers.reconciliation_worker.SessionLocal", return_value=db_session):
        with patch.object(worker.iris_adapter, "get_booking_status") as mock_status:
            iris_ref = sample_booking_command.provider_payload.get("iris_reference")
            mock_status.return_value = {
                "status": "CONFIRMED",
                "iris_reference": iris_ref,
            }

            # Process the case
            await worker._process_single_case(db_session, pending_reconciliation_case)

            # Verify audit events emitted
            audit_events = db_session.query(AuditEvent).all()
            assert len(audit_events) > 0

            # Verify we have either state transition or reconciliation events
            event_types = [e.event_type for e in audit_events]
            assert any(t in ["STATE_TRANSITION", "RECONCILIATION_RESOLVED"] for t in event_types)
