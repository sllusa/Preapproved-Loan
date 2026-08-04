"""Servicing Adapter - Active loan servicing handoff"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class ServicingAdapter:
    """
    Adapter for Active-Loan Servicing Context integration.

    Handles:
    - Loan activation handoff
    - Servicing context projection
    - Post-booking visibility
    """

    def __init__(self, timeout: float = 2.0):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (default: 2s)
        """
        self.base_url = settings.servicing_context_url
        self.timeout = timeout

    def project_active_loan(
        self,
        iris_reference: str,
        customer_id: str,
        entity_id: str,
        amount: float,
        term_months: int,
        tin: float,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Project active loan to servicing context.

        Args:
            iris_reference: IRIS loan reference
            customer_id: Customer identifier
            entity_id: Entity identifier
            amount: Loan amount
            term_months: Loan term in months
            tin: Nominal interest rate
            correlation_id: Optional correlation ID for tracing

        Returns:
            Projection result with keys:
            - servicing_id: Servicing context identifier
            - iris_reference: IRIS loan reference
            - status: Projection status (ACTIVE, PENDING)

        Raises:
            TimeoutError: If request exceeds timeout budget
            ValueError: If API returns error
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "iris_reference": iris_reference,
            "customer_id": customer_id,
            "entity_id": entity_id,
            "amount": amount,
            "term_months": term_months,
            "tin": tin
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/loans/project",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "servicing_id": data.get("servicing_id"),
                    "iris_reference": iris_reference,
                    "status": data.get("status", "ACTIVE")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Servicing projection timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Servicing projection error: {e.response.status_code}"
            ) from e

    def get_loan_status(
        self,
        iris_reference: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get active loan status from servicing context.

        Args:
            iris_reference: IRIS loan reference
            correlation_id: Optional correlation ID for tracing

        Returns:
            Loan status with keys:
            - iris_reference: IRIS loan reference
            - status: Loan status (ACTIVE, CLOSED, DEFAULTED)
            - next_due_date: Next payment due date
            - outstanding_balance: Outstanding principal balance
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/loans/{iris_reference}/status",
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "iris_reference": iris_reference,
                    "status": data.get("status", "UNKNOWN"),
                    "next_due_date": data.get("next_due_date"),
                    "outstanding_balance": data.get("outstanding_balance")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Servicing status retrieval timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {
                    "iris_reference": iris_reference,
                    "status": "NOT_FOUND",
                    "message": "Loan not found in servicing context"
                }
            raise ValueError(
                f"Servicing status retrieval error: {e.response.status_code}"
            ) from e
