"""Preapproved Offer Snapshot model"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, Numeric, String

from app.database import Base


class PreapprovedOfferSnapshot(Base):
    """Retrieved offer evidence for journey start/resume"""
    __tablename__ = "preapproved_offer_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False)
    max_amount = Column(Numeric(15, 2), nullable=False)
    max_term_months = Column(Integer, nullable=False)
    indicative_tin = Column(Numeric(6, 4), nullable=True)
    indicative_tae = Column(Numeric(6, 4), nullable=True)
    validity_ends_at = Column(DateTime, nullable=False)
    offer_status = Column(String(32), nullable=False)
    offer_payload = Column(JSON, nullable=True)
    retrieved_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
