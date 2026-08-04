"""Document Service - Document generation and acknowledgement capture"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import DocumentAcknowledgement, DocumentPackage, EntityConfiguration


class DocumentService:
    """
    Document package generation (SECCI/INE), acknowledgement capture, evidence persistence.
    Integrates with document generation service using versioned legal templates.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_document_package(
        self,
        journey_id: str,
        entity_id: str,
        simulation_amount: float,
        simulation_term_months: int,
        language_code: str = "es"
    ) -> DocumentPackage:
        """
        Generate precontractual and contractual document package.

        Resolves legal package variant (SECCI vs INE) from entity configuration.
        In production, calls document generation adapter.
        """
        # Get entity config to determine legal package mode
        entity_config = self.db.query(EntityConfiguration).filter(
            EntityConfiguration.entity_id == entity_id
        ).first()

        if not entity_config:
            raise ValueError(f"Entity {entity_id} not configured")

        # Determine legal package variant
        legal_package_mode = entity_config.legal_package_mode

        if legal_package_mode not in ["SECCI", "INE"]:
            raise ValueError(
                f"Invalid legal_package_mode: {legal_package_mode}. Must be SECCI or INE"
            )

        # Validate language support
        supported_languages = entity_config.supported_languages or []
        if language_code not in supported_languages:
            language_code = supported_languages[0] if supported_languages else "es"

        # Generate package
        # In production: call document_generation_adapter.generate()
        package_id = f"pkg_{uuid.uuid4().hex[:16]}"

        # Generate package hash
        package_hash = f"hash_{uuid.uuid4().hex[:16]}"

        package = DocumentPackage(
            package_id=package_id,
            journey_id=journey_id,
            variant=legal_package_mode,
            version="1.0",
            language_code=language_code,
            documents=self._generate_mock_documents(legal_package_mode),
            package_hash=package_hash
        )

        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)

        return package

    def _generate_mock_documents(self, variant: str) -> Dict[str, Any]:
        """Generate mock document metadata"""
        if variant == "SECCI":
            return {
                "documents": [
                    {
                        "document_type": "SECCI",
                        "storage_ref": f"docs/secci_{uuid.uuid4().hex[:8]}.pdf",
                        "size_bytes": 45120,
                        "checksum": "mock_checksum_secci"
                    },
                    {
                        "document_type": "CONTRACT",
                        "storage_ref": f"docs/contract_{uuid.uuid4().hex[:8]}.pdf",
                        "size_bytes": 32768,
                        "checksum": "mock_checksum_contract"
                    }
                ]
            }
        else:  # INE
            return {
                "documents": [
                    {
                        "document_type": "INE",
                        "storage_ref": f"docs/ine_{uuid.uuid4().hex[:8]}.pdf",
                        "size_bytes": 48200,
                        "checksum": "mock_checksum_ine"
                    },
                    {
                        "document_type": "CONTRACT",
                        "storage_ref": f"docs/contract_{uuid.uuid4().hex[:8]}.pdf",
                        "size_bytes": 32768,
                        "checksum": "mock_checksum_contract"
                    }
                ]
            }

    def get_document_package(self, package_id: str) -> Optional[DocumentPackage]:
        """Retrieve document package by ID"""
        return self.db.query(DocumentPackage).filter(
            DocumentPackage.package_id == package_id
        ).first()

    def record_acknowledgement(
        self,
        package_id: str,
        journey_id: str,
        customer_id: str,
        acknowledged_at: datetime,
        rights_acknowledged: bool = True
    ) -> DocumentAcknowledgement:
        """
        Record customer acknowledgement of document package.

        Captures immutable evidence of precontractual disclosure.
        """
        acknowledgement = DocumentAcknowledgement(
            package_id=package_id,
            journey_id=journey_id,
            customer_id=customer_id,
            acknowledged_at=acknowledged_at,
            rights_acknowledged=rights_acknowledged
        )

        self.db.add(acknowledgement)
        self.db.commit()
        self.db.refresh(acknowledgement)

        return acknowledgement

    def get_acknowledgement(
        self,
        journey_id: str
    ) -> Optional[DocumentAcknowledgement]:
        """Retrieve document acknowledgement for a journey"""
        return self.db.query(DocumentAcknowledgement).filter(
            DocumentAcknowledgement.journey_id == journey_id
        ).order_by(
            DocumentAcknowledgement.acknowledged_at.desc()
        ).first()
