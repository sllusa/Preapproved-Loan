"""Tests for Journey Orchestrator Service"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import EntityConfiguration
from app.services.journey_orchestrator import JourneyOrchestrator, StateTransitionError


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
    session.commit()

    yield session
    session.close()


def test_create_journey(db_session):
    """Test journey creation"""
    orchestrator = JourneyOrchestrator(db_session)

    journey = orchestrator.create_journey(
        journey_id="journey_001",
        customer_id="cust_001",
        entity_id="test_entity",
        offer_id="offer_001",
        channel="app"
    )

    assert journey.journey_id == "journey_001"
    assert journey.customer_id == "cust_001"
    assert journey.current_state == "OFERTA_VIGENTE"
    assert journey.version == 0


def test_state_machine_prevents_invalid_transition(db_session):
    """Test that state machine prevents invalid transitions"""
    orchestrator = JourneyOrchestrator(db_session)

    # Create journey in CADUCADA (terminal state)
    _journey = orchestrator.create_journey(
        journey_id="journey_002",
        customer_id="cust_002",
        entity_id="test_entity",
        offer_id="offer_002",
        channel="app",
        initial_state="CADUCADA"
    )

    # Attempt invalid transition from CADUCADA to FIRMADO
    with pytest.raises(StateTransitionError) as exc_info:
        orchestrator.apply_transition(
            journey_id="journey_002",
            target_state="FIRMADO",
            trigger="SIGNATURE_COMPLETED"
        )

    assert "Invalid transition" in str(exc_info.value)


def test_state_transition_guards_pendiente_firma(db_session):
    """Test PENDIENTE_FIRMA only reachable from PENDIENTE_VERIFICACIONES"""
    orchestrator = JourneyOrchestrator(db_session)

    # Create journey
    _journey = orchestrator.create_journey(
        journey_id="journey_003",
        customer_id="cust_003",
        entity_id="test_entity",
        offer_id="offer_003",
        channel="web",
        initial_state="PENDIENTE_VERIFICACIONES"
    )

    # Valid transition
    updated = orchestrator.apply_transition(
        journey_id="journey_003",
        target_state="PENDIENTE_FIRMA",
        trigger="CHECKS_PASSED"
    )

    assert updated.current_state == "PENDIENTE_FIRMA"
    assert updated.version == 1


def test_journey_state_progression_happy_path(db_session):
    """Test complete happy path state progression"""
    orchestrator = JourneyOrchestrator(db_session)

    journey = orchestrator.create_journey(
        journey_id="journey_happy",
        customer_id="cust_happy",
        entity_id="test_entity",
        offer_id="offer_happy",
        channel="app"
    )

    # OFERTA_VIGENTE → EN_SIMULACION
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="EN_SIMULACION",
        trigger="SIMULATION_STARTED"
    )
    assert journey.current_state == "EN_SIMULACION"

    # EN_SIMULACION → PENDIENTE_INFORMACION_PRECONTRACTUAL
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="PENDIENTE_INFORMACION_PRECONTRACTUAL",
        trigger="SIMULATION_CONFIRMED"
    )
    assert journey.current_state == "PENDIENTE_INFORMACION_PRECONTRACTUAL"

    # PENDIENTE_INFORMACION_PRECONTRACTUAL → PENDIENTE_VERIFICACIONES
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="PENDIENTE_VERIFICACIONES",
        trigger="DOCUMENTS_ACKNOWLEDGED"
    )
    assert journey.current_state == "PENDIENTE_VERIFICACIONES"

    # PENDIENTE_VERIFICACIONES → PENDIENTE_FIRMA
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="PENDIENTE_FIRMA",
        trigger="CHECKS_PASSED"
    )
    assert journey.current_state == "PENDIENTE_FIRMA"

    # PENDIENTE_FIRMA → FIRMADO
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="FIRMADO",
        trigger="SIGNATURE_COMPLETED"
    )
    assert journey.current_state == "FIRMADO"

    # FIRMADO → ABONADO
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="ABONADO",
        trigger="BOOKING_CONFIRMED"
    )
    assert journey.current_state == "ABONADO"

    # ABONADO → ACTIVO
    journey = orchestrator.apply_transition(
        journey_id="journey_happy",
        target_state="ACTIVO",
        trigger="LOAN_ACTIVATED"
    )
    assert journey.current_state == "ACTIVO"
    assert journey.version == 7  # 7 transitions


def test_is_terminal_state(db_session):
    """Test terminal state detection"""
    orchestrator = JourneyOrchestrator(db_session)

    assert orchestrator.is_terminal_state("ACTIVO")
    assert orchestrator.is_terminal_state("CADUCADA")
    assert orchestrator.is_terminal_state("REVOCADA")
    assert orchestrator.is_terminal_state("RECHAZADA_VERIFICACION")
    assert orchestrator.is_terminal_state("ABANDONADO")
    assert orchestrator.is_terminal_state("DESISTIDO")
    assert orchestrator.is_terminal_state("CANCELADO")

    assert not orchestrator.is_terminal_state("OFERTA_VIGENTE")
    assert not orchestrator.is_terminal_state("EN_SIMULACION")


def test_optimistic_locking(db_session):
    """Test optimistic locking prevents concurrent updates"""
    orchestrator = JourneyOrchestrator(db_session)

    journey = orchestrator.create_journey(
        journey_id="journey_lock",
        customer_id="cust_lock",
        entity_id="test_entity",
        offer_id="offer_lock",
        channel="app"
    )

    # First update with correct version
    journey = orchestrator.apply_transition(
        journey_id="journey_lock",
        target_state="EN_SIMULACION",
        trigger="SIMULATION_STARTED",
        optimistic_version=0
    )
    assert journey.version == 1

    # Second update with stale version should fail
    with pytest.raises(ValueError) as exc_info:
        orchestrator.apply_transition(
            journey_id="journey_lock",
            target_state="PENDIENTE_INFORMACION_PRECONTRACTUAL",
            trigger="SIMULATION_CONFIRMED",
            optimistic_version=0  # Stale version
        )

    assert "Version mismatch" in str(exc_info.value)


def test_update_journey_reference(db_session):
    """Test updating journey reference fields"""
    orchestrator = JourneyOrchestrator(db_session)

    _journey = orchestrator.create_journey(
        journey_id="journey_ref",
        customer_id="cust_ref",
        entity_id="test_entity",
        offer_id="offer_ref",
        channel="app"
    )

    # Update reference fields
    updated = orchestrator.update_journey_reference(
        journey_id="journey_ref",
        active_simulation_id="sim_001",
        selected_account_id="acc_001",
        channel_last_used="web"
    )

    assert updated.active_simulation_id == "sim_001"
    assert updated.selected_account_id == "acc_001"
    assert updated.channel_last_used == "web"
