"""Anti-Fraud Verification Adapter - Fraud screening"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class FraudAdapter:
    """
    Adapter for Anti-Fraud Service integration.

    Handles:
    - Fraud risk screening
    - Transaction pattern analysis
    - Decision normalization (PASS/REJECT/REVIEW)
    """

    def __init__(self, timeout: float = 2.5):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 2500ms)
        """
        self.base_url = settings.fraud_service_url
        self.timeout = timeout

    def screen_fraud_risk(
        self,
        customer_id: str,
        entity_id: str,
        amount: float,
        journey_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform anti-fraud screening.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            amount: Requested loan amount
            journey_id: Journey identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Screening result with keys:
            - decision: PASS | REJECT | REVIEW
            - risk_score: Fraud risk score (0-1 scale)
            - verdict: Risk verdict (LOW_RISK, MEDIUM_RISK, HIGH_RISK)
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
            "journey_id": journey_id
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/screen",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()

                # Normalize decision based on risk score and verdict
                decision = self._normalize_decision(
                    data.get("risk_score"),
                    data.get("verdict")
                )

                return {
                    "decision": decision,
                    "risk_score": data.get("risk_score"),
                    "verdict": data.get("verdict"),
                    "reason_code": data.get("reason_code"),
                    "provider_reference": data.get("provider_reference"),
                    "raw_response": data
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Fraud screening timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Fraud screening error: {e.response.status_code}"
            ) from e

    def _normalize_decision(
        self,
        risk_score: Optional[float],
        verdict: Optional[str]
    ) -> str:
        """
        Normalize fraud screening result to standard decision.

        Args:
            risk_score: Fraud risk score (0-1 scale)
            verdict: Risk verdict string

        Returns:
            Normalized decision: PASS | REJECT | REVIEW
        """
        # Use risk score if available
        if risk_score is not None:
            if risk_score < 0.3:
                return "PASS"
            elif risk_score > 0.7:
                return "REJECT"
            else:
                return "REVIEW"

        # Fall back to verdict
        if verdict:
            verdict_upper = verdict.upper()
            if "LOW" in verdict_upper:
                return "PASS"
            elif "HIGH" in verdict_upper:
                return "REJECT"
            else:
                return "REVIEW"

        # Default to REVIEW for safety
        return "REVIEW"
