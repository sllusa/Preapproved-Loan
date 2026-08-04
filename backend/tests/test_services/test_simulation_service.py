"""Tests for Simulation Service"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import EntityConfiguration, PreapprovedOfferSnapshot
from app.services.simulation_service import SimulationService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)  # noqa: N806
    session = SessionLocal()

    # Seed entity config
    entity_config = EntityConfiguration(
        entity_id="test_entity",
        brand_code="TEST",
        min_amount=1000.00,
        max_term_months=60,
        legal_package_mode="SECCI",
        supported_languages=["es"],
        rollout_flags={},
        config_version="1.0",
        is_active=True
    )
    session.add(entity_config)

    # Seed offer
    from datetime import datetime, timedelta
    offer = PreapprovedOfferSnapshot(
        offer_id="offer_001",
        customer_id="cust_001",
        entity_id="test_entity",
        max_amount=15000.00,
        max_term_months=60,
        indicative_tin=6.50,
        indicative_tae=6.72,
        validity_ends_at=datetime.utcnow() + timedelta(days=30),
        offer_status="ACTIVE"
    )
    session.add(offer)
    session.commit()

    yield session
    session.close()


def test_simulation_validates_amount_within_offer_max(db_session):
    """Test simulation validates amount <= offer.maxAmount"""
    service = SimulationService(db_session)

    # Valid simulation within bounds
    result = service.simulate(
        journey_id="journey_001",
        offer_id="offer_001",
        entity_id="test_entity",
        amount=10000.00,
        term_months=48
    )

    assert result["amount"] == 10000.00
    assert result["term_months"] == 48
    assert "installment_amount" in result


def test_simulation_rejects_amount_exceeding_offer_max(db_session):
    """Test simulation rejects amount > offer.maxAmount"""
    service = SimulationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.simulate(
            journey_id="journey_002",
            offer_id="offer_001",
            entity_id="test_entity",
            amount=20000.00,  # Exceeds max_amount of 15000
            term_months=48
        )

    assert "exceeds offer maximum" in str(exc_info.value)


def test_simulation_validates_term_within_offer_max(db_session):
    """Test simulation validates termMonths <= offer.maxTermMonths"""
    service = SimulationService(db_session)

    # Valid simulation
    result = service.simulate(
        journey_id="journey_003",
        offer_id="offer_001",
        entity_id="test_entity",
        amount=10000.00,
        term_months=60  # Exactly at max
    )

    assert result["term_months"] == 60


def test_simulation_rejects_term_exceeding_offer_max(db_session):
    """Test simulation rejects termMonths > offer.maxTermMonths"""
    service = SimulationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.simulate(
            journey_id="journey_004",
            offer_id="offer_001",
            entity_id="test_entity",
            amount=10000.00,
            term_months=72  # Exceeds max_term_months of 60
        )

    assert "exceeds offer maximum" in str(exc_info.value)


def test_simulation_validates_entity_min_amount(db_session):
    """Test simulation validates amount >= entity.minAmount"""
    service = SimulationService(db_session)

    # Amount below entity minimum
    with pytest.raises(ValueError) as exc_info:
        service.simulate(
            journey_id="journey_005",
            offer_id="offer_001",
            entity_id="test_entity",
            amount=500.00,  # Below min_amount of 1000
            term_months=48
        )

    assert "below entity minimum" in str(exc_info.value)


def test_simulation_calculates_pricing(db_session):
    """Test simulation calculates installment, total cost correctly"""
    service = SimulationService(db_session)

    result = service.simulate(
        journey_id="journey_006",
        offer_id="offer_001",
        entity_id="test_entity",
        amount=12000.00,
        term_months=60
    )

    assert result["amount"] == 12000.00
    assert result["term_months"] == 60
    assert result["tin"] == 6.50
    assert result["tae"] == 6.72
    assert result["installment_amount"] > 0
    assert result["total_cost"] > result["amount"]  # Cost includes interest
    assert result["total_interest"] >= 0


def test_persist_simulation(db_session):
    """Test persisting simulation snapshot"""
    service = SimulationService(db_session)

    snapshot = service.persist_simulation(
        journey_id="journey_007",
        offer_id="offer_001",
        amount=10000.00,
        term_months=48,
        tin=6.50,
        tae=6.72,
        installment_amount=235.50,
        total_cost=11304.00,
        is_confirmed=True
    )

    assert snapshot.simulation_id is not None
    assert snapshot.journey_id == "journey_007"
    assert float(snapshot.amount) == 10000.00
    assert snapshot.is_confirmed is True


def test_get_confirmed_simulation(db_session):
    """Test retrieving confirmed simulation"""
    service = SimulationService(db_session)

    # Create draft simulation
    service.persist_simulation(
        journey_id="journey_008",
        offer_id="offer_001",
        amount=8000.00,
        term_months=36,
        tin=6.50,
        tae=6.72,
        installment_amount=245.00,
        total_cost=8820.00,
        is_confirmed=False
    )

    # Create confirmed simulation
    confirmed = service.persist_simulation(
        journey_id="journey_008",
        offer_id="offer_001",
        amount=10000.00,
        term_months=48,
        tin=6.50,
        tae=6.72,
        installment_amount=235.50,
        total_cost=11304.00,
        is_confirmed=True
    )

    # Retrieve confirmed simulation
    retrieved = service.get_confirmed_simulation("journey_008")

    assert retrieved is not None
    assert retrieved.simulation_id == confirmed.simulation_id
    assert retrieved.is_confirmed is True
