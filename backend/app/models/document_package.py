"""Document Package model"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class DocumentPackage(Base):
    """Generated legal package metadata (SECCI/INE)"""
    __tablename__ = "document_package"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(String(64), unique=True, nullable=False, index=True)
    journey_id = Column(String(64), ForeignKey("journey_instance.id"), nullable=False, index=True)
    variant = Column(String(32), nullable=False)
    version = Column(String(32), nullable=False)
    language_code = Column(String(8), nullable=False)
    documents = Column(JSON, nullable=False)
    package_hash = Column(String(128), nullable=False)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
