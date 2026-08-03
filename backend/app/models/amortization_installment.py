"""Amortization Installment model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database import Base


class AmortizationInstallment(Base):
    """Individual repayment installment details"""
    __tablename__ = "amortization_installment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    installment_id = Column(String(64), unique=True, nullable=False, index=True)
    schedule_id = Column(String(64), ForeignKey("amortization_schedule.schedule_id"), nullable=False, index=True)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_amount = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    outstanding_balance = Column(Numeric(15, 2), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
