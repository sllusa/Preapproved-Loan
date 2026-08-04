"""Outbox Event model - transactional event publication"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.database import Base


class OutboxEvent(Base):
    """Transactional outbox for reliable event emission"""
    __tablename__ = "outbox_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    outbox_event_id = Column(String(64), unique=True, nullable=False, index=True)
    aggregate_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    event_payload = Column(JSON, nullable=False)
    publication_status = Column(String(32), nullable=False, index=True)
    retry_count = Column(Integer, nullable=False, default=0)
    published_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
