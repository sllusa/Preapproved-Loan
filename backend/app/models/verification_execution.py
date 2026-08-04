"""Verification Execution model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class VerificationExecution(Base):
    """Parallel checks execution header"""
    __tablename__ = "verification_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_execution_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    normalized_decision = Column(String(32), nullable=False)
    reason_code = Column(String(64), nullable=True)
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
