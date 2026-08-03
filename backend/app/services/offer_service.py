"""Offer Service - Offer retrieval and eligibility normalization"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import EntityConfiguration, JourneyInstance, PreapprovedOfferSnapshot


class OfferService:
    """
    Offer retrieval, normalization, expiry/revocation revalidation.
    Integrates with Pre-Approval Engine (via adapter).
    """

    def __init__(self, db: Session):
        self.db = db

    def retrieve_offers(
        self,
        customer_id: str,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve actionable offers for a customer.

        In production, this would call the Pre-Approval Engine adapter.
        For now, returns mock data for testing.
        """
        # Get entity config to validate min amount
        entity_config = self.db.query(EntityConfiguration).filter(
            EntityConfiguration.entity_id == entity_id
        ).first()

        if not entity_config:
            raise ValueError(f"Entity {entity_id} not configured")

        # Mock offer data (in production: call pre_approval_adapter)
        mock_offers = [
            {
                "offer_id": f"offer_{customer_id}_001",
                "max_amount": 15000.00,
                "max_term_months": 60,
                "indicative_tin": 6.50,
                "indicative_tae": 6.72,
                "validity_ends_at": datetime.utcnow().isoformat(),
                "offer_status": "ACTIVE"
            }
        ]

        # Normalize offers - filter by entity minimum
        actionable_offers = []
        for offer in mock_offers:
            # Check if offer meets entity minimum
            if float(offer["max_amount"]) < float(entity_config.min_amount):
                offer["offer_status"] = "NON_ACTIONABLE"
                offer["reason"] = "BELOW_ENTITY_MINIMUM"
            else:
                offer["offer_status"] = "ACTIONABLE"

            actionable_offers.append(offer)

        return actionable_offers

    def persist_offer_snapshot(
        self,
        offer_id: str,
        customer_id: str,
        entity_id: str,
        max_amount: float,
        max_term_months: int,
        indicative_tin: float,
        indicative_tae: float,
        validity_ends_at: datetime,
        status: str,
        correlation_id: str
    ) -> PreapprovedOfferSnapshot:
        """Persist offer snapshot for journey start/resume"""
        snapshot = PreapprovedOfferSnapshot(
            offer_id=offer_id,
            customer_id=customer_id,
            entity_id=entity_id,
            max_amount=max_amount,
            max_term_months=max_term_months,
            indicative_tin=indicative_tin,
            indicative_tae=indicative_tae,
            validity_ends_at=validity_ends_at,
            status=status,
            correlation_id=correlation_id
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def get_offer_snapshot(self, offer_id: str) -> Optional[PreapprovedOfferSnapshot]:
        """Retrieve offer snapshot by ID"""
        return self.db.query(PreapprovedOfferSnapshot).filter(
            PreapprovedOfferSnapshot.offer_id == offer_id
        ).first()

    def revalidate_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Revalidate offer status on resume or before sensitive transitions.

        In production, this would call the Pre-Approval Engine adapter.
        """
        snapshot = self.get_offer_snapshot(offer_id)
        if not snapshot:
            return {"valid": False, "reason": "OFFER_NOT_FOUND"}

        # Check expiry
        if snapshot.validity_ends_at and snapshot.validity_ends_at < datetime.utcnow():
            return {"valid": False, "reason": "EXPIRED"}

        # In production: call pre_approval_adapter.check_offer_status()
        # For now, assume valid if not expired
        return {"valid": True, "offer_status": snapshot.status}

    def check_existing_journey(
        self,
        customer_id: str,
        offer_id: str
    ) -> Optional[JourneyInstance]:
        """Check if customer has existing journey for this offer"""
        return self.db.query(JourneyInstance).filter(
            JourneyInstance.customer_id == customer_id,
            JourneyInstance.offer_id == offer_id
        ).order_by(
            JourneyInstance.created_at.desc()
        ).first()
