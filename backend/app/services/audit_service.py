"""Audit Service - Immutable audit event persistence"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import AuditEvent, OutboxEvent


class AuditService:
    """
    Captures immutable audit events for compliance evidence.
    Implements append-only audit ledger with outbox pattern for reliable event emission.
    """

    def __init__(self, db: Session):
        self.db = db

    def emit_event(
        self,
        journey_id: str,
        customer_id: str,
        entity_id: str,
        event_type: str,
        actor_type: str,
        payload: Dict[str, Any],
        correlation_id: str,
        event_id: Optional[str] = None
    ) -> AuditEvent:
        """
        Emit immutable audit event.

        Args:
            journey_id: Journey identifier
            customer_id: Customer identifier (masked for PII protection)
            entity_id: Entity identifier
            event_type: Event type (STATE_TRANSITION, DOCUMENT_ACKNOWLEDGED, etc.)
            actor_type: Actor type (CUSTOMER, SYSTEM, OPERATOR)
            payload: Event payload (will be hashed for immutability)
            correlation_id: Correlation identifier for distributed tracing
            event_id: Optional explicit event ID

        Returns:
            Created audit event
        """
        # Generate payload hash for immutability verification
        payload_hash = self._hash_payload(payload)

        # Create audit event
        audit_event = AuditEvent(
            event_id=event_id or self._generate_event_id(),
            journey_id=journey_id,
            customer_id=customer_id,
            entity_id=entity_id,
            event_type=event_type,
            actor_type=actor_type,
            payload_hash=payload_hash,
            emitted_at=datetime.utcnow(),
            correlation_id=correlation_id
        )

        self.db.add(audit_event)

        # Create outbox event for reliable publication
        outbox_event = OutboxEvent(
            outbox_event_id=f"outbox_{uuid.uuid4().hex[:16]}",
            aggregate_id=journey_id,
            event_type=event_type,
            event_payload=json.dumps(payload),
            publication_status="PENDING"
        )

        self.db.add(outbox_event)

        # Commit in same transaction
        self.db.commit()
        self.db.refresh(audit_event)

        return audit_event

    def get_journey_audit_trail(
        self,
        journey_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditEvent]:
        """Retrieve audit events for a journey"""
        return self.db.query(AuditEvent).filter(
            AuditEvent.journey_id == journey_id
        ).order_by(
            AuditEvent.emitted_at.desc()
        ).limit(limit).offset(offset).all()

    def get_customer_audit_trail(
        self,
        customer_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditEvent]:
        """Retrieve audit events for a customer"""
        return self.db.query(AuditEvent).filter(
            AuditEvent.customer_id == customer_id
        ).order_by(
            AuditEvent.emitted_at.desc()
        ).limit(limit).offset(offset).all()

    def search_events(
        self,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditEvent]:
        """Search audit events with filters"""
        query = self.db.query(AuditEvent)

        if event_type:
            query = query.filter(AuditEvent.event_type == event_type)
        if entity_id:
            query = query.filter(AuditEvent.entity_id == entity_id)
        if start_date:
            query = query.filter(AuditEvent.emitted_at >= start_date)
        if end_date:
            query = query.filter(AuditEvent.emitted_at <= end_date)

        return query.order_by(
            AuditEvent.emitted_at.desc()
        ).limit(limit).offset(offset).all()

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        """Generate deterministic hash of payload"""
        # Sort keys for deterministic hashing
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return f"evt_{uuid.uuid4().hex}"
