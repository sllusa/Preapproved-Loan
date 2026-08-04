"""Signature Session model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class SignatureSession(Base):
    """SCA signature session tracking"""
    __tablename__ = "signature_session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signature_session_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    provider_reference = Column(String(128), nullable=True, index=True)
    sca_redirect_url = Column(String(512), nullable=True)
    status = Column(String(32), nullable=False)
    signed_contract_digest = Column(String(128), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
