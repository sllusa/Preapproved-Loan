"""Amortization Schedule Adapter - Schedule generation and retrieval"""
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class AmortizationAdapter:
    """
    Adapter for Amortization Schedule Service integration.

    Handles:
    - French amortization schedule generation
    - Schedule retrieval for active loans
    - Installment breakdown
    """

    def __init__(self, timeout: float = 2.0):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 2000ms)
        """
        self.base_url = settings.amortization_service_url
        self.timeout = timeout

    def generate_schedule(
        self,
        loan_id: str,
        amount: float,
        term_months: int,
        tin: float,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate French amortization schedule.

        Args:
            loan_id: Loan identifier
            amount: Loan principal amount
            term_months: Loan term in months
            tin: Nominal interest rate (annual)
            correlation_id: Optional correlation ID for tracing

        Returns:
            Schedule result with keys:
            - schedule_id: Generated schedule identifier
            - loan_id: Loan identifier
            - installments: List of installment dictionaries
            - total_interest: Total interest payable
            - total_cost: Total cost (principal + interest)

        Raises:
            TimeoutError: If request exceeds timeout budget
            ValueError: If API returns error
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "loan_id": loan_id,
            "amount": amount,
            "term_months": term_months,
            "tin": tin
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/schedule/generate",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "schedule_id": data.get("schedule_id"),
                    "loan_id": loan_id,
                    "installments": data.get("installments", []),
                    "total_interest": data.get("total_interest"),
                    "total_cost": data.get("total_cost")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Amortization schedule generation timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Amortization schedule generation error: {e.response.status_code}"
            ) from e

    def get_schedule(
        self,
        loan_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve existing amortization schedule.

        Args:
            loan_id: Loan identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Schedule with installment breakdown
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/schedule/{loan_id}",
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "schedule_id": data.get("schedule_id"),
                    "loan_id": loan_id,
                    "installments": data.get("installments", []),
                    "total_interest": data.get("total_interest"),
                    "total_cost": data.get("total_cost")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Amortization schedule retrieval timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Schedule not found for loan {loan_id}") from e
            raise ValueError(
                f"Amortization schedule retrieval error: {e.response.status_code}"
            ) from e

    def normalize_installments(
        self,
        raw_installments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize installment list for service layer.

        Args:
            raw_installments: Raw installment data from amortization service

        Returns:
            Normalized installment list with standardized fields
        """
        normalized = []

        for installment in raw_installments:
            normalized_installment = {
                "installment_number": installment.get("installment_number"),
                "due_date": installment.get("due_date"),
                "principal": float(installment.get("principal", 0)),
                "interest": float(installment.get("interest", 0)),
                "total_payment": float(installment.get("total_payment", 0)),
                "remaining_balance": float(installment.get("remaining_balance", 0))
            }

            normalized.append(normalized_installment)

        return normalized
