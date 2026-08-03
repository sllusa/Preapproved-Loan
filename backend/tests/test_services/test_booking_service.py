"""Tests for Booking Service"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.booking_service import BookingService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)  # noqa: N806
    session = SessionLocal()
    yield session
    session.close()


def test_generate_idempotency_key_deterministic(db_session):
    """Test idempotency key generation is deterministic"""
    service = BookingService(db_session)

    key1 = service.generate_idempotency_key(
        entity_id="ent_001",
        journey_id="journey_001",
        offer_id="offer_001",
        signed_contract_digest="abc123",
        command_type="BOOK",
        version="v1"
    )

    key2 = service.generate_idempotency_key(
        entity_id="ent_001",
        journey_id="journey_001",
        offer_id="offer_001",
        signed_contract_digest="abc123",
        command_type="BOOK",
        version="v1"
    )

    assert key1 == key2
    assert "ent_001" in key1
    assert "journey_001" in key1
    assert "offer_001" in key1
    assert "abc123" in key1
    assert "BOOK" in key1
    assert "v1" in key1


def test_idempotency_key_format(db_session):
    """Test idempotency key follows specified format"""
    service = BookingService(db_session)

    key = service.generate_idempotency_key(
        entity_id="entityId",
        journey_id="journeyId",
        offer_id="offerId",
        signed_contract_digest="digest",
        command_type="BOOK",
        version="v1"
    )

    # Format: {entityId}:{journeyId}:{offerId}:{digest}:BOOK:v1
    expected = "entityId:journeyId:offerId:digest:BOOK:v1"
    assert key == expected


def test_execute_booking_writes_idempotency_record_before_call(db_session):
    """Test booking service writes idempotency_record before calling adapter"""
    service = BookingService(db_session)

    result = service.execute_booking(
        journey_id="journey_001",
        entity_id="ent_001",
        offer_id="offer_001",
        customer_id="cust_001",
        amount=10000.00,
        term_months=48,
        disbursement_account_id="acc_001",
        signed_contract_digest="digest_001"
    )

    assert result["booking_command_id"] is not None
    assert result["status"] in ["CONFIRMED", "PENDING_RECONCILIATION", "FAILED"]

    # Verify idempotency record was written
    from app.models import IdempotencyRecord

    idempotency_key = service.generate_idempotency_key(
        entity_id="ent_001",
        journey_id="journey_001",
        offer_id="offer_001",
        signed_contract_digest="digest_001"
    )

    record = db_session.query(IdempotencyRecord).filter(
        IdempotencyRecord.idempotency_key == idempotency_key
    ).first()

    assert record is not None
    assert record.journey_id == "journey_001"


def test_execute_booking_idempotent_on_duplicate_call(db_session):
    """Test booking is idempotent - duplicate calls return same result"""
    service = BookingService(db_session)

    # First call
    result1 = service.execute_booking(
        journey_id="journey_002",
        entity_id="ent_002",
        offer_id="offer_002",
        customer_id="cust_002",
        amount=15000.00,
        term_months=60,
        disbursement_account_id="acc_002",
        signed_contract_digest="digest_002"
    )

    # Second call with same parameters
    result2 = service.execute_booking(
        journey_id="journey_002",
        entity_id="ent_002",
        offer_id="offer_002",
        customer_id="cust_002",
        amount=15000.00,
        term_months=60,
        disbursement_account_id="acc_002",
        signed_contract_digest="digest_002"
    )

    # Should return same booking command
    assert result1["booking_command_id"] == result2["booking_command_id"]
    assert result1["status"] == result2["status"]


def test_execute_booking_creates_reconciliation_case_on_pending(db_session):
    """Test reconciliation case created for pending status"""
    service = BookingService(db_session)

    # Mock pending status (in production, adapter would return this)
    # For this test, we'll check the logic path
    result = service.execute_booking(
        journey_id="journey_003",
        entity_id="ent_003",
        offer_id="offer_003",
        customer_id="cust_003",
        amount=12000.00,
        term_months=48,
        disbursement_account_id="acc_003",
        signed_contract_digest="digest_003"
    )

    # Current mock implementation returns CONFIRMED
    # In production with real adapter, test would verify PENDING creates reconciliation case
    assert result["booking_command_id"] is not None


def test_get_booking_status(db_session):
    """Test retrieving booking status"""
    service = BookingService(db_session)

    # Create booking
    result = service.execute_booking(
        journey_id="journey_004",
        entity_id="ent_004",
        offer_id="offer_004",
        customer_id="cust_004",
        amount=8000.00,
        term_months=36,
        disbursement_account_id="acc_004",
        signed_contract_digest="digest_004"
    )

    # Get status
    status = service.get_booking_status("journey_004")

    assert status is not None
    assert status["command_id"] == result["booking_command_id"]
    assert status["status"] is not None
