"""Simulation Service - Real-time pricing simulation"""
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import EntityConfiguration, PreapprovedOfferSnapshot, SimulationSnapshot


class SimulationService:
    """
    Stateless simulation API with amount/term validation and snapshot persistence.
    In production, integrates with pricing adapter for real-time calculations.
    """

    def __init__(self, db: Session):
        self.db = db

    def simulate(
        self,
        journey_id: str,
        offer_id: str,
        entity_id: str,
        amount: float,
        term_months: int,
        selected_account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform real-time simulation with validation.

        Args:
            journey_id: Journey identifier
            offer_id: Offer identifier
            entity_id: Entity identifier
            amount: Requested loan amount
            term_months: Requested loan term in months
            selected_account_id: Optional selected disbursement account

        Returns:
            Simulation result with calculated values

        Raises:
            ValueError: If validation fails
        """
        # Validate against offer bounds
        offer = self.db.query(PreapprovedOfferSnapshot).filter(
            PreapprovedOfferSnapshot.offer_id == offer_id
        ).first()

        if not offer:
            raise ValueError(f"Offer {offer_id} not found")

        if amount > float(offer.max_amount):
            raise ValueError(
                f"Amount {amount} exceeds offer maximum {offer.max_amount}"
            )

        if term_months > offer.max_term_months:
            raise ValueError(
                f"Term {term_months} months exceeds offer maximum {offer.max_term_months} months"
            )

        # Validate against entity configuration bounds
        entity_config = self.db.query(EntityConfiguration).filter(
            EntityConfiguration.entity_id == entity_id
        ).first()

        if not entity_config:
            raise ValueError(f"Entity {entity_id} not configured")

        if amount < float(entity_config.min_amount):
            raise ValueError(
                f"Amount {amount} below entity minimum {entity_config.min_amount}"
            )

        if term_months > entity_config.max_term_months:
            raise ValueError(
                f"Term {term_months} months exceeds entity maximum {entity_config.max_term_months} months"
            )

        # Perform pricing calculation
        # In production: call pricing_adapter.calculate()
        # For now, use simple fixed-rate calculation
        simulation_result = self._calculate_pricing(
            amount=amount,
            term_months=term_months,
            tin=float(offer.indicative_tin),
            tae=float(offer.indicative_tae)
        )

        return simulation_result

    def _calculate_pricing(
        self,
        amount: float,
        term_months: int,
        tin: float,
        tae: float
    ) -> Dict[str, Any]:
        """
        Calculate loan pricing.
        Simplified French amortization schedule calculation.
        """
        # Monthly interest rate
        monthly_rate = tin / 100 / 12

        # Calculate monthly installment using amortization formula
        if monthly_rate > 0:
            installment = amount * (
                monthly_rate * (1 + monthly_rate) ** term_months
            ) / (
                (1 + monthly_rate) ** term_months - 1
            )
        else:
            # Zero interest case
            installment = amount / term_months

        total_cost = installment * term_months
        total_interest = total_cost - amount

        return {
            "amount": round(amount, 2),
            "term_months": term_months,
            "tin": tin,
            "tae": tae,
            "installment_amount": round(installment, 2),
            "total_cost": round(total_cost, 2),
            "total_interest": round(total_interest, 2)
        }

    def persist_simulation(
        self,
        journey_id: str,
        offer_id: str,
        amount: float,
        term_months: int,
        tin: float,
        tae: float,
        installment_amount: float,
        total_cost: float,
        selected_account_id: Optional[str] = None,
        is_confirmed: bool = False
    ) -> SimulationSnapshot:
        """Persist simulation snapshot"""
        simulation_id = f"sim_{uuid.uuid4().hex[:16]}"

        snapshot = SimulationSnapshot(
            simulation_id=simulation_id,
            journey_id=journey_id,
            offer_id=offer_id,
            amount=Decimal(str(amount)),
            term_months=term_months,
            tin=Decimal(str(tin)),
            tae=Decimal(str(tae)),
            installment_amount=Decimal(str(installment_amount)),
            total_cost=Decimal(str(total_cost)),
            selected_account_id=selected_account_id,
            is_confirmed=is_confirmed
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def get_simulation(self, simulation_id: str) -> Optional[SimulationSnapshot]:
        """Retrieve simulation snapshot by ID"""
        return self.db.query(SimulationSnapshot).filter(
            SimulationSnapshot.simulation_id == simulation_id
        ).first()

    def get_latest_simulation(self, journey_id: str) -> Optional[SimulationSnapshot]:
        """Get latest simulation for a journey"""
        return self.db.query(SimulationSnapshot).filter(
            SimulationSnapshot.journey_id == journey_id
        ).order_by(
            SimulationSnapshot.created_at.desc()
        ).first()

    def get_confirmed_simulation(self, journey_id: str) -> Optional[SimulationSnapshot]:
        """Get confirmed simulation for a journey"""
        return self.db.query(SimulationSnapshot).filter(
            SimulationSnapshot.journey_id == journey_id,
            SimulationSnapshot.is_confirmed
        ).order_by(
            SimulationSnapshot.created_at.desc()
        ).first()
