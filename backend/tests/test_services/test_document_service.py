"""Tests for Document Service"""
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import EntityConfiguration
from app.services.document_service import DocumentService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)  # noqa: N806
    session = SessionLocal()

    # Seed SECCI entity
    entity_secci = EntityConfiguration(
        entity_id="entity_secci",
        brand_code="SECCI",
        min_amount=1000.00,
        max_term_months=60,
        legal_package_mode="SECCI",
        supported_languages=["es", "ca"],
        rollout_flags={},
        config_version="1.0",
        is_active=True
    )
    session.add(entity_secci)

    # Seed INE entity
    entity_ine = EntityConfiguration(
        entity_id="entity_ine",
        brand_code="INE",
        min_amount=1000.00,
        max_term_months=60,
        legal_package_mode="INE",
        supported_languages=["es"],
        rollout_flags={},
        config_version="1.0",
        is_active=True
    )
    session.add(entity_ine)

    session.commit()

    yield session
    session.close()


def test_document_service_resolves_secci_mode(db_session):
    """Test document service resolves SECCI legal package variant from entity config"""
    service = DocumentService(db_session)

    package = service.generate_document_package(
        journey_id="journey_secci",
        entity_id="entity_secci",
        simulation_amount=10000.00,
        simulation_term_months=48,
        language_code="es"
    )

    assert package.variant == "SECCI"
    assert package.journey_id == "journey_secci"
    assert package.language_code == "es"
    assert "documents" in package.documents

    # Check SECCI documents are present
    docs = package.documents["documents"]
    doc_types = [d["document_type"] for d in docs]
    assert "SECCI" in doc_types
    assert "CONTRACT" in doc_types


def test_document_service_resolves_ine_mode(db_session):
    """Test document service resolves INE legal package variant from entity config"""
    service = DocumentService(db_session)

    package = service.generate_document_package(
        journey_id="journey_ine",
        entity_id="entity_ine",
        simulation_amount=12000.00,
        simulation_term_months=60,
        language_code="es"
    )

    assert package.variant == "INE"
    assert package.journey_id == "entity_ine"

    # Check INE documents are present
    docs = package.documents["documents"]
    doc_types = [d["document_type"] for d in docs]
    assert "INE" in doc_types
    assert "CONTRACT" in doc_types


def test_document_service_validates_unsupported_language(db_session):
    """Test document service falls back to supported language"""
    service = DocumentService(db_session)

    # Request unsupported language
    package = service.generate_document_package(
        journey_id="journey_lang",
        entity_id="entity_ine",
        simulation_amount=10000.00,
        simulation_term_months=48,
        language_code="en"  # Not supported by entity_ine
    )

    # Should fallback to first supported language
    assert package.language_code == "es"


def test_record_acknowledgement(db_session):
    """Test recording document acknowledgement"""
    service = DocumentService(db_session)

    # Generate package
    package = service.generate_document_package(
        journey_id="journey_ack",
        entity_id="entity_secci",
        simulation_amount=10000.00,
        simulation_term_months=48
    )

    # Record acknowledgement
    acknowledged_at = datetime.utcnow()
    ack = service.record_acknowledgement(
        package_id=package.package_id,
        journey_id="journey_ack",
        customer_id="cust_ack",
        acknowledged_at=acknowledged_at,
        rights_acknowledged=True
    )

    assert ack.package_id == package.package_id
    assert ack.journey_id == "journey_ack"
    assert ack.customer_id == "cust_ack"
    assert ack.rights_acknowledged is True


def test_get_acknowledgement(db_session):
    """Test retrieving document acknowledgement"""
    service = DocumentService(db_session)

    # Generate and acknowledge
    package = service.generate_document_package(
        journey_id="journey_get_ack",
        entity_id="entity_secci",
        simulation_amount=10000.00,
        simulation_term_months=48
    )

    service.record_acknowledgement(
        package_id=package.package_id,
        journey_id="journey_get_ack",
        customer_id="cust_get_ack",
        acknowledged_at=datetime.utcnow()
    )

    # Retrieve acknowledgement
    retrieved = service.get_acknowledgement("journey_get_ack")

    assert retrieved is not None
    assert retrieved.journey_id == "journey_get_ack"
    assert retrieved.package_id == package.package_id
