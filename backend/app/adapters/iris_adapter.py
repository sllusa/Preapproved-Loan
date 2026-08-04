"""IRIS Core and Disbursement Adapter - Booking and disbursement orchestration"""
from typing import Any, Dict, Optional

import httpx

from app.config import settings


class IRISAdapter:
    """
    Adapter for IRIS Core and Disbursement API integration.

    Handles:
    - Idempotent loan booking
    - Disbursement command submission
    - Status polling and reconciliation
    - Timeout handling with no blind retries
    """

    def __init__(
        self,
        booking_timeout: float = 4.0,
        status_timeout: float = 2.0
    ):
        """
        Initialize adapter with separate timeout budgets.

        Args:
            booking_timeout: Booking request timeout in seconds (LLD: 4000ms)
            status_timeout: Status polling timeout in seconds (LLD: 2000ms)
        """
        self.base_url = settings.iris_api_url
        self.booking_timeout = booking_timeout
        self.status_timeout = status_timeout

    def book_loan(
        self,
        idempotency_key: str,
        customer_id: str,
        entity_id: str,
        amount: float,
        term_months: int,
        disbursement_account_id: str,
        contract_reference: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit idempotent booking command to IRIS.

        Args:
            idempotency_key: Deterministic idempotency key
            customer_id: Customer identifier
            entity_id: Entity identifier
            amount: Loan amount
            term_months: Loan term in months
            disbursement_account_id: Target disbursement account
            contract_reference: Signed contract reference
            correlation_id: Optional correlation ID for tracing

        Returns:
            Booking response with keys:
            - status: CONFIRMED | PENDING | FAILED
            - iris_reference: IRIS loan reference (if CONFIRMED or PENDING)
            - error_code: Error code (if FAILED)
            - message: Human-readable message

        Raises:
            TimeoutError: If request exceeds booking timeout
            ValueError: If API returns error or uncertain response
        """
        headers = {"X-Idempotency-Key": idempotency_key}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "customer_id": customer_id,
            "entity_id": entity_id,
            "amount": amount,
            "term_months": term_months,
            "disbursement_account_id": disbursement_account_id,
            "contract_reference": contract_reference
        }

        try:
            with httpx.Client(timeout=self.booking_timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/booking",
                    json=payload,
                    headers=headers
                )

                # Handle successful booking
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    return {
                        "status": "CONFIRMED",
                        "iris_reference": data.get("iris_reference"),
                        "message": "Booking confirmed"
                    }

                # Handle accepted but pending confirmation
                elif response.status_code == 202:
                    data = response.json()
                    return {
                        "status": "PENDING",
                        "iris_reference": data.get("iris_reference"),
                        "message": "Booking pending confirmation"
                    }

                # Handle explicit failure
                elif response.status_code >= 400:
                    data = response.json() if response.text else {}
                    return {
                        "status": "FAILED",
                        "error_code": data.get("error_code", "BOOKING_FAILED"),
                        "message": data.get("message", f"HTTP {response.status_code}")
                    }

                # Handle unexpected status
                else:
                    return {
                        "status": "PENDING",
                        "message": f"Uncertain response: HTTP {response.status_code}"
                    }

        except httpx.TimeoutException as e:
            # Timeout = uncertain state, requires reconciliation
            raise TimeoutError(
                f"IRIS booking timeout after {self.booking_timeout}s - requires reconciliation"
            ) from e
        except httpx.RequestError as e:
            # Network error = uncertain state
            raise ValueError(
                f"IRIS booking network error - requires reconciliation: {str(e)}"
            ) from e

    def get_booking_status(
        self,
        iris_reference: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Poll booking status from IRIS.

        Args:
            iris_reference: IRIS loan reference from booking
            correlation_id: Optional correlation ID for tracing

        Returns:
            Status response with keys:
            - status: CONFIRMED | PENDING | FAILED
            - iris_reference: IRIS loan reference
            - disbursement_status: COMPLETED | IN_PROGRESS | FAILED (if available)
            - message: Human-readable message
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.status_timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/booking/{iris_reference}/status",
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "status": data.get("status", "UNKNOWN"),
                    "iris_reference": iris_reference,
                    "disbursement_status": data.get("disbursement_status"),
                    "message": data.get("message", "")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"IRIS status poll timeout after {self.status_timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            # 404 might mean booking not found or not yet replicated
            if e.response.status_code == 404:
                return {
                    "status": "UNKNOWN",
                    "iris_reference": iris_reference,
                    "message": "Booking not found"
                }
            raise ValueError(
                f"IRIS status poll error: {e.response.status_code}"
            ) from e

    def submit_disbursement(
        self,
        iris_reference: str,
        disbursement_account_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit disbursement command for a booked loan.

        Args:
            iris_reference: IRIS loan reference from booking
            disbursement_account_id: Target account for disbursement
            correlation_id: Optional correlation ID for tracing

        Returns:
            Disbursement response with keys:
            - status: SUBMITTED | FAILED
            - message: Human-readable message
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "iris_reference": iris_reference,
            "disbursement_account_id": disbursement_account_id
        }

        try:
            with httpx.Client(timeout=self.booking_timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/disbursement",
                    json=payload,
                    headers=headers
                )

                if response.status_code in (200, 201, 202):
                    return {
                        "status": "SUBMITTED",
                        "message": "Disbursement submitted"
                    }
                else:
                    data = response.json() if response.text else {}
                    return {
                        "status": "FAILED",
                        "message": data.get("message", f"HTTP {response.status_code}")
                    }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"IRIS disbursement timeout after {self.booking_timeout}s"
            ) from e
        except httpx.RequestError as e:
            raise ValueError(
                f"IRIS disbursement network error: {str(e)}"
            ) from e
