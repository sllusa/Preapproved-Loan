"""Signature Service - PSD2/SCA signature orchestration"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import SignatureSession


class SignatureService:
    """
    PSD2/SCA signature orchestration, callback handling, signed-state transition enforcement.
    Integrates with external SCA signature provider.
    """

    def __init__(self, db: Session):
        self.db = db

    def initiate_signature(
        self,
        journey_id: str,
        customer_id: str,
        contract_digest: str,
        callback_url: str
    ) -> SignatureSession:
        """
        Initiate SCA signature session.

        In production, calls SCA signature provider adapter.
        Returns session with redirect URL for customer authentication.
        """
        session_id = f"sig_{uuid.uuid4().hex[:16]}"

        # In production: call sca_adapter.initiate_signature()
        # For now, generate mock redirect URL
        redirect_url = f"https://sca-provider.example.com/sign?session={session_id}"

        # Session expires in 15 minutes
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        session = SignatureSession(
            session_id=session_id,
            journey_id=journey_id,
            customer_id=customer_id,
            contract_digest=contract_digest,
            status="INITIATED",
            redirect_url=redirect_url,
            expires_at=expires_at
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def handle_callback(
        self,
        session_id: str,
        provider_reference: str,
        status: str,
        completed_at: Optional[datetime] = None
    ) -> SignatureSession:
        """
        Handle SCA provider callback after signature completion.

        Args:
            session_id: Signature session identifier
            provider_reference: Provider's signature reference
            status: Signature status (SUCCESS, FAILED, CANCELLED)
            completed_at: When signature was completed

        Returns:
            Updated signature session
        """
        session = self.db.query(SignatureSession).filter(
            SignatureSession.session_id == session_id
        ).first()

        if not session:
            raise ValueError(f"Signature session {session_id} not found")

        # Check if session has expired
        if session.expires_at and datetime.utcnow() > session.expires_at:
            session.status = "EXPIRED"
            self.db.commit()
            raise ValueError(f"Signature session {session_id} has expired")

        # Update session with callback data
        session.provider_reference = provider_reference
        session.status = status
        session.completed_at = completed_at or datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        return session

    def get_signature_session(
        self,
        session_id: str
    ) -> Optional[SignatureSession]:
        """Retrieve signature session by ID"""
        return self.db.query(SignatureSession).filter(
            SignatureSession.session_id == session_id
        ).first()

    def get_journey_signature(
        self,
        journey_id: str
    ) -> Optional[SignatureSession]:
        """Get latest signature session for a journey"""
        return self.db.query(SignatureSession).filter(
            SignatureSession.journey_id == journey_id
        ).order_by(
            SignatureSession.created_at.desc()
        ).first()

    def verify_signature_status(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Verify signature session status.

        Returns normalized status for state transition guards.
        """
        session = self.get_signature_session(session_id)

        if not session:
            return {
                "valid": False,
                "reason": "SESSION_NOT_FOUND"
            }

        if session.status == "SUCCESS":
            return {
                "valid": True,
                "status": "SIGNED",
                "provider_reference": session.provider_reference,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
        elif session.status == "EXPIRED":
            return {
                "valid": False,
                "reason": "SESSION_EXPIRED"
            }
        elif session.status == "FAILED":
            return {
                "valid": False,
                "reason": "SIGNATURE_FAILED"
            }
        elif session.status == "CANCELLED":
            return {
                "valid": False,
                "reason": "SIGNATURE_CANCELLED"
            }
        else:
            return {
                "valid": False,
                "reason": "SIGNATURE_PENDING",
                "status": session.status
            }
