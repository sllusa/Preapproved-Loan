"""Idempotency Record model"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String

from app.database import Base


class IdempotencyRecord(Base):
    """Booking/disbursement command idempotency registry"""
    __tablename__ = "idempotency_record"

    idempotency_key = Column(String(255), primary_key=True)
    entity_id = Column(String(64), nullable=False)
    journey_id = Column(String(64), nullable=False, index=True)
    command_type = Column(String(32), nullable=False)
    request_hash = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    iris_operation_ref = Column(String(128), nullable=True)
    first_submitted_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    response_snapshot = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
