"""SCA Signature Adapter - PSD2/SCA strong customer authentication"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class SCAAdapter:
    """
    Adapter for PSD2/SCA Signature Service integration.

    Handles:
    - Signature session initiation
    - Redirect URL generation
    - Callback status handling
    - Signature completion verification

    Note: Timeout is provider-driven, not enforced by this adapter.
    """

    def __init__(self, timeout: float = 5.0):
        """
        Initialize adapter with default timeout.

        Args:
            timeout: Request timeout in seconds (default: 5s for initiation)
        """
        self.base_url = settings.sca_signature_url
        self.timeout = timeout

    def initiate_signature(
        self,
        customer_id: str,
        entity_id: str,
        journey_id: str,
        contract_digest: str,
        callback_url: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate SCA signature session.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            journey_id: Journey identifier
            contract_digest: Signed contract digest
            callback_url: Callback URL for completion notification
            correlation_id: Optional correlation ID for tracing

        Returns:
            Session initiation result with keys:
            - session_id: Provider session identifier
            - redirect_url: URL to redirect customer for authentication
            - expires_at: Session expiry timestamp
            - status: Session status (INITIATED)

        Raises:
            TimeoutError: If request exceeds timeout budget
            ValueError: If API returns error
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "customer_id": customer_id,
            "entity_id": entity_id,
            "journey_id": journey_id,
            "contract_digest": contract_digest,
            "callback_url": callback_url
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/signature/initiate",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "session_id": data.get("session_id"),
                    "redirect_url": data.get("redirect_url"),
                    "expires_at": data.get("expires_at"),
                    "status": "INITIATED"
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"SCA signature initiation timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"SCA signature initiation error: {e.response.status_code}"
            ) from e

    def verify_signature(
        self,
        session_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify signature session status.

        Args:
            session_id: Provider session identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Verification result with keys:
            - session_id: Provider session identifier
            - status: Session status (SUCCESS, FAILED, PENDING, EXPIRED, CANCELLED)
            - provider_reference: Provider signature reference (if SUCCESS)
            - completed_at: Signature completion timestamp (if SUCCESS)
            - reason: Failure reason (if FAILED)
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/signature/{session_id}/status",
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "session_id": session_id,
                    "status": data.get("status", "UNKNOWN"),
                    "provider_reference": data.get("provider_reference"),
                    "completed_at": data.get("completed_at"),
                    "reason": data.get("reason")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"SCA signature verification timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            # 404 might mean session not found
            if e.response.status_code == 404:
                return {
                    "session_id": session_id,
                    "status": "NOT_FOUND",
                    "reason": "Session not found"
                }
            raise ValueError(
                f"SCA signature verification error: {e.response.status_code}"
            ) from e

    def normalize_callback_status(
        self,
        raw_status: str
    ) -> str:
        """
        Normalize provider callback status to standard values.

        Args:
            raw_status: Raw status from provider callback

        Returns:
            Normalized status: SUCCESS | FAILED | CANCELLED | EXPIRED
        """
        raw_upper = raw_status.upper()

        success_variants = {"SUCCESS", "COMPLETED", "SIGNED", "OK"}
        failed_variants = {"FAILED", "ERROR", "REJECTED"}
        cancelled_variants = {"CANCELLED", "ABORTED", "USER_CANCELLED"}
        expired_variants = {"EXPIRED", "TIMEOUT"}

        if raw_upper in success_variants:
            return "SUCCESS"
        elif raw_upper in failed_variants:
            return "FAILED"
        elif raw_upper in cancelled_variants:
            return "CANCELLED"
        elif raw_upper in expired_variants:
            return "EXPIRED"
        else:
            # Unknown statuses default to FAILED for safety
            return "FAILED"
