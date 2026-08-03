"""Disbursement Account Selection model"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class DisbursementAccountSelection(Base):
    """Selected disbursement account with operability validation"""
    __tablename__ = "disbursement_account_selection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    selection_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    account_id = Column(String(64), nullable=False)
    iban_masked = Column(String(64), nullable=False)
    account_type = Column(String(32), nullable=True)
    is_operable = Column(Boolean, nullable=False)
    failure_reason_code = Column(String(64), nullable=True)
    validated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
