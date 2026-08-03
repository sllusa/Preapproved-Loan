"""Booking Command model"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class BookingCommand(Base):
    """IRIS booking command attempts and outcomes"""
    __tablename__ = "booking_command"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_command_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    idempotency_key = Column(String(255), ForeignKey("idempotency_record.idempotency_key"), nullable=False, index=True)
    provider_status = Column(String(32), nullable=False)
    booking_status = Column(String(32), nullable=False)
    pending_reconciliation = Column(Boolean, nullable=False, default=False)
    last_error_code = Column(String(64), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    provider_payload = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
