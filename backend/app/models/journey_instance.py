"""Journey Instance model - canonical process aggregate"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class JourneyInstance(Base):
    """Canonical journey state aggregate with lifecycle tracking"""
    __tablename__ = "journey_instance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), ForeignKey("entity_configuration.entity_id"), nullable=False)
    offer_id = Column(String(64), nullable=False)
    current_state = Column(String(64), nullable=False, index=True)
    channel_last_used = Column(String(16), nullable=False)

    # References to related aggregates
    active_simulation_id = Column(String(64), nullable=True)
    selected_account_id = Column(String(64), nullable=True)
    document_package_id = Column(String(64), nullable=True)
    verification_execution_id = Column(String(64), nullable=True)
    signature_session_id = Column(String(64), nullable=True)
    latest_booking_command_id = Column(String(64), nullable=True)

    # Optimistic locking and resume control
    version = Column(Integer, nullable=False, default=0)
    resume_deadline_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("customer_id", "offer_id", "current_state", name="uq_journey_customer_offer_state"),
    )
