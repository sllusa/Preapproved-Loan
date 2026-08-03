"""Amortization Schedule model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class AmortizationSchedule(Base):
    """Loan repayment schedule header"""
    __tablename__ = "amortization_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(String(64), unique=True, nullable=False, index=True)
    loan_id = Column(String(64), ForeignKey("loan_activation_projection.loan_id"), nullable=False, index=True)
    currency = Column(String(3), nullable=False)
    installment_count = Column(Integer, nullable=False)
    first_due_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
