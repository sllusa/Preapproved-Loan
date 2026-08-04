"""Loan Activation Projection model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class LoanActivationProjection(Base):
    """Loan activation and servicing readiness projection"""
    __tablename__ = "loan_activation_projection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    servicing_reference = Column(String(128), nullable=True)
    schedule_id = Column(String(64), nullable=True)
    activation_status = Column(String(32), nullable=False)
    activated_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
