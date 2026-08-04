"""Notification Service - Customer messaging and notification orchestration"""
import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Customer notification orchestration for journey milestones, status updates, and exception handling.

    In production, integrates with notification providers (email, SMS, push).
    For now, provides logging-based notification simulation.
    """

    def __init__(self, db: Session):
        self.db = db

    def send_notification(
        self,
        customer_id: str,
        notification_type: str,
        channel: str,
        subject: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification to customer.

        Args:
            customer_id: Customer identifier
            notification_type: Type of notification (JOURNEY_MILESTONE, STATUS_UPDATE, etc.)
            channel: Delivery channel (EMAIL, SMS, PUSH)
            subject: Notification subject
            message: Notification message body
            context: Additional context data

        Returns:
            Notification delivery result
        """
        # In production: call notification provider adapter
        # For now, log the notification
        logger.info(
            f"Notification sent to customer {customer_id} via {channel}: "
            f"[{notification_type}] {subject} - {message}"
        )

        return {
            "notification_id": f"notif_{customer_id}_{notification_type}",
            "customer_id": customer_id,
            "channel": channel,
            "status": "SENT",
            "notification_type": notification_type
        }

    def notify_offer_available(
        self,
        customer_id: str,
        offer_amount: float,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer that pre-approved offer is available"""
        return self.send_notification(
            customer_id=customer_id,
            notification_type="OFFER_AVAILABLE",
            channel=channel,
            subject="Tu préstamo pre-aprobado está disponible",
            message=f"Tienes una oferta de préstamo pre-aprobado de hasta {offer_amount}€. "
                    f"Accede a tu app para simular y solicitar tu préstamo."
        )

    def notify_verification_complete(
        self,
        customer_id: str,
        journey_id: str,
        decision: str,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer of verification outcome"""
        if decision == "PASS":
            subject = "Verificación completada - Continúa con tu solicitud"
            message = "Las verificaciones de tu solicitud han sido completadas exitosamente. " \
                     "Ya puedes continuar con la firma de tu préstamo."
        else:
            subject = "Actualización sobre tu solicitud"
            message = "Necesitamos revisar tu solicitud. Nos pondremos en contacto contigo pronto."

        return self.send_notification(
            customer_id=customer_id,
            notification_type="VERIFICATION_COMPLETE",
            channel=channel,
            subject=subject,
            message=message,
            context={"journey_id": journey_id, "decision": decision}
        )

    def notify_signature_required(
        self,
        customer_id: str,
        journey_id: str,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer that signature is required"""
        return self.send_notification(
            customer_id=customer_id,
            notification_type="SIGNATURE_REQUIRED",
            channel=channel,
            subject="Firma tu préstamo",
            message="Tu solicitud está lista para firmar. Accede a tu app para completar la firma digital.",
            context={"journey_id": journey_id}
        )

    def notify_loan_disbursed(
        self,
        customer_id: str,
        journey_id: str,
        amount: float,
        account: str,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer of successful disbursement"""
        return self.send_notification(
            customer_id=customer_id,
            notification_type="LOAN_DISBURSED",
            channel=channel,
            subject="Tu préstamo ha sido desembolsado",
            message=f"Hemos transferido {amount}€ a tu cuenta {account}. "
                    f"El dinero estará disponible en las próximas 24 horas.",
            context={"journey_id": journey_id, "amount": amount}
        )

    def notify_pending_reconciliation(
        self,
        customer_id: str,
        journey_id: str,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer that disbursement is being processed"""
        return self.send_notification(
            customer_id=customer_id,
            notification_type="PENDING_RECONCILIATION",
            channel=channel,
            subject="Procesando tu préstamo",
            message="Estamos procesando tu préstamo. Te notificaremos cuando esté completado. "
                    "Esto puede tomar hasta 24 horas.",
            context={"journey_id": journey_id}
        )

    def notify_journey_expired(
        self,
        customer_id: str,
        journey_id: str,
        channel: str = "EMAIL"
    ) -> Dict[str, Any]:
        """Notify customer that journey has expired"""
        return self.send_notification(
            customer_id=customer_id,
            notification_type="JOURNEY_EXPIRED",
            channel=channel,
            subject="Tu solicitud ha expirado",
            message="Tu solicitud de préstamo ha expirado. Puedes iniciar una nueva solicitud cuando lo desees.",
            context={"journey_id": journey_id}
        )
