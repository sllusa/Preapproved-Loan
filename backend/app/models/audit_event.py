"""Audit Event model - immutable append-only ledger"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.database import Base


class AuditEvent(Base):
    """Immutable audit event ledger for compliance evidence"""
    __tablename__ = "audit_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    actor_type = Column(String(32), nullable=False)
    payload_hash = Column(String(128), nullable=True)
    event_payload = Column(JSON, nullable=True)
    correlation_id = Column(String(128), nullable=True, index=True)
    emitted_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Note: This table is append-only. No UPDATE or DELETE operations allowed.
