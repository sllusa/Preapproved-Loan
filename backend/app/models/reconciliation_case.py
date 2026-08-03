"""Reconciliation Case model"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class ReconciliationCase(Base):
    """Pending timeout/uncertain IRIS booking resolution cases"""
    __tablename__ = "reconciliation_case"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reconciliation_case_id = Column(String(64), unique=True, nullable=False, index=True, default=lambda: f"recon_{uuid.uuid4().hex[:16]}")
    journey_id = Column(String(64), ForeignKey("journey_instance.journey_id"), nullable=False, index=True)
    booking_command_id = Column(String(64), ForeignKey("booking_command.booking_command_id"), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True)
    last_polled_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    operator_assigned_at = Column(DateTime, nullable=True)
    support_reference = Column(String(128), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
