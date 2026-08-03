"""AML/PBC Verification Adapter - Anti-money laundering and PEP screening"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class AMLAdapter:
    """
    Adapter for AML/PBC Service integration.

    Handles:
    - Anti-money laundering screening
    - Politically exposed person (PEP) checks
    - Sanctions list matching
    - Decision normalization (PASS/REJECT/REVIEW)
    """

    def __init__(self, timeout: float = 2.5):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 2500ms)
        """
        self.base_url = settings.aml_service_url
        self.timeout = timeout

    def screen_aml_pbc(
        self,
        customer_id: str,
        entity_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform AML/PBC screening.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Screening result with keys:
            - decision: PASS | REJECT | REVIEW
            - pep_match: Boolean PEP match indicator
            - sanctions_match: Boolean sanctions match indicator
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
            "entity_id": entity_id
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

                # Normalize decision based on match indicators
                decision = self._normalize_decision(
                    data.get("pep_match", False),
                    data.get("sanctions_match", False)
                )

                return {
                    "decision": decision,
                    "pep_match": data.get("pep_match", False),
                    "sanctions_match": data.get("sanctions_match", False),
                    "reason_code": data.get("reason_code"),
                    "provider_reference": data.get("provider_reference"),
                    "raw_response": data
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"AML/PBC screening timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"AML/PBC screening error: {e.response.status_code}"
            ) from e

    def _normalize_decision(
        self,
        pep_match: bool,
        sanctions_match: bool
    ) -> str:
        """
        Normalize AML/PBC screening result to standard decision.

        Args:
            pep_match: PEP match indicator
            sanctions_match: Sanctions match indicator

        Returns:
            Normalized decision: PASS | REJECT | REVIEW
        """
        # Sanctions match = automatic reject
        if sanctions_match:
            return "REJECT"

        # PEP match = manual review required
        if pep_match:
            return "REVIEW"

        # No matches = pass
        return "PASS"
