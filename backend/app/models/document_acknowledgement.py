"""Document Acknowledgement model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class DocumentAcknowledgement(Base):
    """Customer acknowledgement evidence for document packages"""
    __tablename__ = "document_acknowledgement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    acknowledgement_id = Column(String(64), unique=True, nullable=False, index=True)
    package_id = Column(String(64), ForeignKey("document_package.package_id"), nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False)
    acknowledged_at = Column(DateTime, nullable=False)
    actor_type = Column(String(32), nullable=False)
    ip_address = Column(String(64), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
