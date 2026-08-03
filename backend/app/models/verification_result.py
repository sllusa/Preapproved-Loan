"""Verification Result model"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class VerificationResult(Base):
    """Individual provider verification outcomes"""
    __tablename__ = "verification_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_result_id = Column(String(64), unique=True, nullable=False, index=True)
    verification_execution_id = Column(String(64), ForeignKey("verification_execution.verification_execution_id"), nullable=False, index=True)
    provider_type = Column(String(32), nullable=False)
    provider_decision = Column(String(32), nullable=False)
    provider_payload = Column(JSON, nullable=True)
    provider_correlation_id = Column(String(128), nullable=True)
    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
