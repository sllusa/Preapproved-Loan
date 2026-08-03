"""Creditworthiness Verification Adapter - Light creditworthiness checks"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class CreditworthinessAdapter:
    """
    Adapter for Creditworthiness Service integration.

    Handles:
    - Light creditworthiness verification
    - Credit score retrieval
    - Decision normalization (PASS/REJECT/REVIEW)
    """

    def __init__(self, timeout: float = 2.5):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 2500ms)
        """
        self.base_url = settings.creditworthiness_service_url
        self.timeout = timeout

    def verify_creditworthiness(
        self,
        customer_id: str,
        entity_id: str,
        amount: float,
        term_months: int,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform light creditworthiness verification.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            amount: Requested loan amount
            term_months: Requested loan term
            correlation_id: Optional correlation ID for tracing

        Returns:
            Verification result with keys:
            - decision: PASS | REJECT | REVIEW
            - score: Credit score (if available)
            - rating: Credit rating (if available)
            - reason_code: Decision reason code
            - provider_reference: Provider transaction reference

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
            "amount": amount,
            "term_months": term_months
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/verify",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()

                # Normalize decision
                raw_decision = data.get("decision", "UNKNOWN")
                decision = self._normalize_decision(raw_decision)

                return {
                    "decision": decision,
                    "score": data.get("score"),
                    "rating": data.get("rating"),
                    "reason_code": data.get("reason_code"),
                    "provider_reference": data.get("provider_reference"),
                    "raw_response": data
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Creditworthiness verification timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Creditworthiness verification error: {e.response.status_code}"
            ) from e

    def _normalize_decision(self, raw_decision: str) -> str:
        """
        Normalize heterogeneous provider decisions to standard values.

        Args:
            raw_decision: Raw decision from provider

        Returns:
            Normalized decision: PASS | REJECT | REVIEW
        """
        raw_upper = raw_decision.upper()

        # Map various provider responses to standard decisions
        pass_variants = {"PASS", "APPROVED", "ACCEPT", "OK", "SUCCESS"}
        reject_variants = {"REJECT", "DECLINED", "DENIED", "FAIL", "FAILED"}
        review_variants = {"REVIEW", "MANUAL", "PENDING", "REFERRED"}

        if raw_upper in pass_variants:
            return "PASS"
        elif raw_upper in reject_variants:
            return "REJECT"
        elif raw_upper in review_variants:
            return "REVIEW"
        else:
            # Unknown decisions default to REVIEW for safety
            return "REVIEW"
