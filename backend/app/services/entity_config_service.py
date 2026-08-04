"""Entity Configuration Service - Multi-entity parameterization"""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import EntityConfiguration


class EntityConfigService:
    """
    Multi-entity configuration management via ParametrizacionEntidad.
    Provides entity-specific product parameters, branding, language, and legal text.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_entity_config(
        self,
        entity_id: str
    ) -> Optional[EntityConfiguration]:
        """Retrieve entity configuration by ID"""
        return self.db.query(EntityConfiguration).filter(
            EntityConfiguration.entity_id == entity_id
        ).first()

    def get_active_entities(self) -> List[EntityConfiguration]:
        """Retrieve all active entity configurations"""
        return self.db.query(EntityConfiguration).filter(
            EntityConfiguration.is_active
        ).all()

    def validate_entity_active(
        self,
        entity_id: str
    ) -> bool:
        """Check if entity is active and configured"""
        config = self.get_entity_config(entity_id)
        return config is not None and config.is_active

    def get_legal_package_mode(
        self,
        entity_id: str
    ) -> Optional[str]:
        """Get legal package mode (SECCI or INE) for entity"""
        config = self.get_entity_config(entity_id)
        return config.legal_package_mode if config else None

    def get_supported_languages(
        self,
        entity_id: str
    ) -> List[str]:
        """Get supported languages for entity"""
        config = self.get_entity_config(entity_id)
        if not config or not config.supported_languages:
            return ["es"]  # Default to Spanish
        return config.supported_languages

    def get_product_limits(
        self,
        entity_id: str
    ) -> Dict[str, Any]:
        """Get product limits for entity"""
        config = self.get_entity_config(entity_id)
        if not config:
            raise ValueError(f"Entity {entity_id} not configured")

        return {
            "min_amount": float(config.min_amount),
            "max_term_months": config.max_term_months
        }

    def check_rollout_flag(
        self,
        entity_id: str,
        flag_name: str
    ) -> bool:
        """Check entity rollout flag value"""
        config = self.get_entity_config(entity_id)
        if not config or not config.rollout_flags:
            return False

        return config.rollout_flags.get(flag_name, False)

    def create_entity_config(
        self,
        entity_id: str,
        brand_code: str,
        min_amount: float,
        max_term_months: int,
        legal_package_mode: str,
        supported_languages: List[str],
        rollout_flags: Dict[str, Any],
        config_version: str = "1.0",
        is_active: bool = True
    ) -> EntityConfiguration:
        """Create new entity configuration"""
        if legal_package_mode not in ["SECCI", "INE"]:
            raise ValueError("legal_package_mode must be SECCI or INE")

        config = EntityConfiguration(
            entity_id=entity_id,
            brand_code=brand_code,
            min_amount=min_amount,
            max_term_months=max_term_months,
            legal_package_mode=legal_package_mode,
            supported_languages=supported_languages,
            rollout_flags=rollout_flags,
            config_version=config_version,
            is_active=is_active
        )

        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)

        return config

    def update_entity_config(
        self,
        entity_id: str,
        **kwargs
    ) -> EntityConfiguration:
        """Update entity configuration"""
        config = self.get_entity_config(entity_id)
        if not config:
            raise ValueError(f"Entity {entity_id} not found")

        allowed_fields = {
            "brand_code",
            "min_amount",
            "max_term_months",
            "legal_package_mode",
            "supported_languages",
            "rollout_flags",
            "config_version",
            "is_active"
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(config, key, value)

        self.db.commit()
        self.db.refresh(config)

        return config
