"""Journey Orchestrator Service - Canonical state machine enforcement"""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import JourneyInstance
from app.services.audit_service import AuditService


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""
    pass


class JourneyOrchestrator:
    """
    Enforces lifecycle state machine with guarded transitions and audit event emission.

    Main path states:
    OFERTA_VIGENTE → EN_SIMULACION → PENDIENTE_INFORMACION_PRECONTRACTUAL →
    PENDIENTE_VERIFICACIONES → PENDIENTE_FIRMA → FIRMADO → ABONADO → ACTIVO

    Terminal exception states:
    CADUCADA, REVOCADA, RECHAZADA_VERIFICACION, ABANDONADO, DESISTIDO, CANCELADO
    """

    # State machine definitions
    MAIN_PATH_STATES = [
        "OFERTA_VIGENTE",
        "EN_SIMULACION",
        "PENDIENTE_INFORMACION_PRECONTRACTUAL",
        "PENDIENTE_VERIFICACIONES",
        "PENDIENTE_FIRMA",
        "FIRMADO",
        "ABONADO",
        "ACTIVO",
    ]

    TERMINAL_STATES = [
        "CADUCADA",
        "REVOCADA",
        "RECHAZADA_VERIFICACION",
        "ABANDONADO",
        "DESISTIDO",
        "CANCELADO",
    ]

    # Allowed transitions: source -> list of valid target states
    ALLOWED_TRANSITIONS = {
        "OFERTA_VIGENTE": ["EN_SIMULACION", "CADUCADA", "REVOCADA", "ABANDONADO"],
        "EN_SIMULACION": ["PENDIENTE_INFORMACION_PRECONTRACTUAL", "CADUCADA", "REVOCADA", "ABANDONADO"],
        "PENDIENTE_INFORMACION_PRECONTRACTUAL": ["PENDIENTE_VERIFICACIONES", "CADUCADA", "REVOCADA", "ABANDONADO"],
        "PENDIENTE_VERIFICACIONES": ["PENDIENTE_FIRMA", "RECHAZADA_VERIFICACION", "CADUCADA", "REVOCADA", "ABANDONADO"],
        "PENDIENTE_FIRMA": ["FIRMADO", "CADUCADA", "REVOCADA", "ABANDONADO", "DESISTIDO"],
        "FIRMADO": ["ABONADO", "CANCELADO"],
        "ABONADO": ["ACTIVO"],
        # Terminal states cannot transition
        "ACTIVO": [],
        "CADUCADA": [],
        "REVOCADA": [],
        "RECHAZADA_VERIFICACION": [],
        "ABANDONADO": [],
        "DESISTIDO": [],
        "CANCELADO": [],
    }

    def __init__(self, db: Session, audit_service: Optional[AuditService] = None):
        self.db = db
        self.audit_service = audit_service or AuditService(db)

    def create_journey(
        self,
        journey_id: str,
        customer_id: str,
        entity_id: str,
        offer_id: str,
        channel: str,
        initial_state: str = "OFERTA_VIGENTE"
    ) -> JourneyInstance:
        """Create a new journey instance"""
        journey = JourneyInstance(
            journey_id=journey_id,
            customer_id=customer_id,
            entity_id=entity_id,
            offer_id=offer_id,
            current_state=initial_state,
            channel_last_used=channel,
            version=0
        )

        try:
            self.db.add(journey)
            self.db.commit()
            self.db.refresh(journey)

            # Emit audit event for journey creation
            self.audit_service.emit_event(
                journey_id=journey_id,
                customer_id=customer_id,
                entity_id=entity_id,
                event_type="JOURNEY_CREATED",
                actor_type="CUSTOMER",
                payload={"initial_state": initial_state, "channel": channel},
                correlation_id=journey_id
            )

            return journey
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Journey creation failed: {str(e)}")

    def get_journey(self, journey_id: str) -> Optional[JourneyInstance]:
        """Retrieve journey by ID"""
        return self.db.query(JourneyInstance).filter(
            JourneyInstance.journey_id == journey_id
        ).first()

    def apply_transition(
        self,
        journey_id: str,
        target_state: str,
        trigger: str,
        actor_type: str = "SYSTEM",
        context: Optional[Dict[str, Any]] = None,
        optimistic_version: Optional[int] = None
    ) -> JourneyInstance:
        """
        Apply state transition with guards and audit emission.

        Args:
            journey_id: Journey identifier
            target_state: Desired target state
            trigger: Business event that triggered the transition
            actor_type: Who initiated the transition (CUSTOMER, SYSTEM, OPERATOR)
            context: Additional context for audit
            optimistic_version: Expected version for optimistic locking

        Returns:
            Updated journey instance

        Raises:
            StateTransitionError: If transition is invalid
            ValueError: If journey not found or version mismatch
        """
        journey = self.get_journey(journey_id)
        if not journey:
            raise ValueError(f"Journey {journey_id} not found")

        # Optimistic locking check
        if optimistic_version is not None and journey.version != optimistic_version:
            raise ValueError(
                f"Version mismatch: expected {optimistic_version}, got {journey.version}"
            )

        # Validate transition
        self._validate_transition(journey.current_state, target_state)

        # Store old state for audit
        old_state = journey.current_state

        # Apply transition
        journey.current_state = target_state
        journey.version += 1
        journey.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(journey)

            # Emit audit event for state transition
            self.audit_service.emit_event(
                journey_id=journey_id,
                customer_id=journey.customer_id,
                entity_id=journey.entity_id,
                event_type="STATE_TRANSITION",
                actor_type=actor_type,
                payload={
                    "old_state": old_state,
                    "new_state": target_state,
                    "trigger": trigger,
                    "context": context or {}
                },
                correlation_id=journey_id
            )

            return journey
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"State transition failed: {str(e)}")

    def _validate_transition(self, current_state: str, target_state: str) -> None:
        """
        Validate that a state transition is allowed.

        Args:
            current_state: Current journey state
            target_state: Desired target state

        Raises:
            StateTransitionError: If transition is not allowed
        """
        if current_state not in self.ALLOWED_TRANSITIONS:
            raise StateTransitionError(f"Unknown state: {current_state}")

        allowed = self.ALLOWED_TRANSITIONS[current_state]
        if target_state not in allowed:
            raise StateTransitionError(
                f"Invalid transition from {current_state} to {target_state}. "
                f"Allowed targets: {', '.join(allowed)}"
            )

    def is_terminal_state(self, state: str) -> bool:
        """Check if a state is terminal (no further transitions allowed)"""
        return state in self.TERMINAL_STATES or state == "ACTIVO"

    def update_journey_reference(
        self,
        journey_id: str,
        **kwargs
    ) -> JourneyInstance:
        """
        Update journey reference fields (simulation_id, account_id, etc.) without state change.

        Args:
            journey_id: Journey identifier
            **kwargs: Fields to update (active_simulation_id, selected_account_id, etc.)
        """
        journey = self.get_journey(journey_id)
        if not journey:
            raise ValueError(f"Journey {journey_id} not found")

        # Update allowed reference fields
        allowed_fields = {
            "active_simulation_id",
            "selected_account_id",
            "document_package_id",
            "verification_execution_id",
            "signature_session_id",
            "latest_booking_command_id",
            "channel_last_used",
            "resume_deadline_at"
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(journey, key, value)

        journey.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(journey)
            return journey
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Journey update failed: {str(e)}")
