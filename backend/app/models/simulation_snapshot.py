"""Simulation Snapshot model"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database import Base


class SimulationSnapshot(Base):
    """Confirmed and draft simulation versions"""
    __tablename__ = "simulation_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    term_months = Column(Integer, nullable=False)
    tin = Column(Numeric(6, 4), nullable=False)
    tae = Column(Numeric(6, 4), nullable=False)
    installment_amount = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    pricing_correlation_metadata = Column(JSON, nullable=True)
    simulated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
