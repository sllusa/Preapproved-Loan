"""Pre-Approval Engine Adapter - Offer retrieval and eligibility"""
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class PreApprovalAdapter:
    """
    Adapter for Pre-Approval Engine integration.

    Handles:
    - Offer retrieval by customer
    - Offer status revalidation
    - Expiry and revocation checking
    - Eligibility normalization
    """

    def __init__(self, timeout: float = 1.5):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 1500ms)
        """
        self.base_url = settings.pre_approval_engine_url
        self.timeout = timeout

    def get_offers(
        self,
        customer_id: str,
        entity_id: str,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve pre-approved offers for a customer.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of offer dictionaries with keys:
            - offer_id: Unique offer identifier
            - max_amount: Maximum loan amount
            - max_term_months: Maximum term in months
            - indicative_tin: Indicative nominal interest rate
            - indicative_tae: Indicative APR
            - validity_ends_at: Offer expiry timestamp
            - status: Offer status (ACTIVE, EXPIRED, REVOKED)

        Raises:
            httpx.TimeoutException: If request exceeds timeout budget
            httpx.HTTPStatusError: If API returns error status
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/offers",
                    params={"customer_id": customer_id, "entity_id": entity_id},
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return data.get("offers", [])

        except httpx.TimeoutException as e:
            # Log timeout and re-raise
            raise TimeoutError(
                f"Pre-Approval Engine timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            # Normalize HTTP errors
            raise ValueError(
                f"Pre-Approval Engine error: {e.response.status_code}"
            ) from e

    def check_offer_status(
        self,
        offer_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Revalidate offer status and check for revocation.

        Args:
            offer_id: Offer identifier to validate
            correlation_id: Optional correlation ID for tracing

        Returns:
            Status dictionary with keys:
            - offer_id: Offer identifier
            - status: Current status (ACTIVE, EXPIRED, REVOKED)
            - validity_ends_at: Expiry timestamp (if ACTIVE)
            - revoked_at: Revocation timestamp (if REVOKED)
            - reason: Status reason code
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/offers/{offer_id}/status",
                    headers=headers
                )
                response.raise_for_status()

                return response.json()

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Pre-Approval Engine timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Pre-Approval Engine error: {e.response.status_code}"
            ) from e

    def normalize_offer(
        self,
        raw_offer: Dict[str, Any],
        entity_min_amount: float
    ) -> Dict[str, Any]:
        """
        Normalize offer response and apply entity-specific filtering.

        Args:
            raw_offer: Raw offer data from Pre-Approval Engine
            entity_min_amount: Minimum amount from entity configuration

        Returns:
            Normalized offer with actionability determination
        """
        offer = {
            "offer_id": raw_offer.get("offer_id"),
            "max_amount": float(raw_offer.get("max_amount", 0)),
            "max_term_months": int(raw_offer.get("max_term_months", 0)),
            "indicative_tin": float(raw_offer.get("indicative_tin", 0)),
            "indicative_tae": float(raw_offer.get("indicative_tae", 0)),
            "validity_ends_at": raw_offer.get("validity_ends_at"),
            "status": raw_offer.get("status", "UNKNOWN")
        }

        # Determine actionability
        if offer["max_amount"] < entity_min_amount:
            offer["actionable"] = False
            offer["reason"] = "BELOW_ENTITY_MINIMUM"
        elif offer["status"] != "ACTIVE":
            offer["actionable"] = False
            offer["reason"] = f"STATUS_{offer['status']}"
        else:
            # Check expiry
            validity_ends = offer.get("validity_ends_at")
            if validity_ends:
                try:
                    expiry = datetime.fromisoformat(validity_ends.replace('Z', '+00:00'))
                    if expiry < datetime.utcnow().replace(tzinfo=expiry.tzinfo):
                        offer["actionable"] = False
                        offer["reason"] = "EXPIRED"
                    else:
                        offer["actionable"] = True
                except Exception:
                    offer["actionable"] = False
                    offer["reason"] = "INVALID_EXPIRY"
            else:
                offer["actionable"] = True

        return offer
