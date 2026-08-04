"""Idempotent seed data script"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
import app.models  # noqa: F401 - Import to register all models with Base
from app.models.entity_configuration import EntityConfiguration
from app.models.journey_instance import JourneyInstance
from app.models.preapproved_offer_snapshot import PreapprovedOfferSnapshot
from app.models.user import User


def seed_users(db: Session):
    """Seed default admin user - idempotent"""
    # Check if admin user already exists
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_admin:
        print("  ✓ Admin user already exists")
        return

    # Create default admin user
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        entity_id="ENTITY001",
        is_active=True,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    print("  ✓ Created admin user: admin@example.com / admin123")


def seed_entity_configurations(db: Session):
    """Seed entity configurations - idempotent"""
    # Check if entity configuration already exists
    existing_entity = db.query(EntityConfiguration).filter(
        EntityConfiguration.entity_id == "ENTITY001"
    ).first()
    if existing_entity:
        print("  ✓ Entity configuration already exists")
        return

    # Create active entity configuration
    entity_config = EntityConfiguration(
        entity_id="ENTITY001",
        brand_code="RURALVIA",
        min_amount=1000.00,
        max_term_months=120,
        legal_package_mode="SECCI",
        supported_languages=["es", "ca", "gl", "eu"],
        rollout_flags={
            "enable_digital_signature": True,
            "enable_document_download": True,
            "enable_multi_offer": False
        },
        config_version="1.0.0",
        is_active=True
    )
    db.add(entity_config)
    db.commit()
    print("  ✓ Created active entity configuration: ENTITY001")


def seed_sample_offers(db: Session):
    """Seed sample pre-approved offers - idempotent"""
    # Check if sample offers already exist
    existing_offer = db.query(PreapprovedOfferSnapshot).filter(
        PreapprovedOfferSnapshot.offer_id == "OFFER001"
    ).first()
    if existing_offer:
        print("  ✓ Sample offers already exist")
        return

    # Create sample pre-approved offer
    sample_offer = PreapprovedOfferSnapshot(
        offer_id="OFFER001",
        customer_id="customer_001",
        entity_id="ENTITY001",
        max_amount=15000.00,
        max_term_months=60,
        indicative_tin=0.0599,
        indicative_tae=0.0615,
        validity_ends_at=datetime.now() + timedelta(days=30),
        offer_status="ELIGIBLE",
        offer_payload={"source": "pre_approval_engine", "risk_score": 750},
        retrieved_at=datetime.now()
    )
    db.add(sample_offer)

    # Create another sample offer
    sample_offer_2 = PreapprovedOfferSnapshot(
        offer_id="OFFER002",
        customer_id="customer_002",
        entity_id="ENTITY001",
        max_amount=25000.00,
        max_term_months=84,
        indicative_tin=0.0649,
        indicative_tae=0.0670,
        validity_ends_at=datetime.now() + timedelta(days=45),
        offer_status="ELIGIBLE",
        offer_payload={"source": "pre_approval_engine", "risk_score": 820},
        retrieved_at=datetime.now()
    )
    db.add(sample_offer_2)

    db.commit()
    print("  ✓ Created 2 sample pre-approved offers")


def seed_sample_journeys(db: Session):
    """Seed sample journey instances - idempotent"""
    # Check if sample journeys already exist
    existing_journey = db.query(JourneyInstance).filter(
        JourneyInstance.journey_id == "JOURNEY001"
    ).first()
    if existing_journey:
        print("  ✓ Sample journeys already exist")
        return

    # Create sample journey in OFERTA_VIGENTE state
    sample_journey = JourneyInstance(
        journey_id="JOURNEY001",
        customer_id="customer_001",
        entity_id="ENTITY001",
        offer_id="OFFER001",
        current_state="OFERTA_VIGENTE",
        channel_last_used="APP",
        version=1
    )
    db.add(sample_journey)

    # Create another sample journey in SIMULACION_GUARDADA state
    sample_journey_2 = JourneyInstance(
        journey_id="JOURNEY002",
        customer_id="customer_002",
        entity_id="ENTITY001",
        offer_id="OFFER002",
        current_state="SIMULACION_GUARDADA",
        channel_last_used="WEB",
        version=1
    )
    db.add(sample_journey_2)

    db.commit()
    print("  ✓ Created 2 sample journey instances")


def run_seed():
    """
    Execute seed data - idempotent operation.

    Seeds:
    - Default admin user (admin@example.com / admin123)
    - At least one active entity configuration (ENTITY001)
    - Sample pre-approved offers
    - Sample journey instances

    All seeding operations are idempotent - checks existence before insert.
    """
    print("\n🌱 Running seed data...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed in dependency order
        seed_entity_configurations(db)
        seed_users(db)
        seed_sample_offers(db)
        seed_sample_journeys(db)

        print("✅ Seed data completed successfully\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
