"""Entity Configuration model"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, Numeric, String

from app.database import Base


class EntityConfiguration(Base):
    """Multi-entity parameterization configuration"""
    __tablename__ = "entity_configuration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String(64), unique=True, nullable=False, index=True)
    brand_code = Column(String(64), nullable=False)
    min_amount = Column(Numeric(15, 2), nullable=False)
    max_term_months = Column(Integer, nullable=False)
    legal_package_mode = Column(String(32), nullable=False)
    supported_languages = Column(JSON, nullable=False)
    rollout_flags = Column(JSON, nullable=False)
    config_version = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
