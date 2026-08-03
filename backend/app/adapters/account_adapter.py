"""Account Validation Adapter - Disbursement account selection and operability"""
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class AccountAdapter:
    """
    Adapter for Account Validation Service integration.

    Handles:
    - Eligible account listing
    - Account operability validation
    - Blocking rule enforcement
    """

    def __init__(self, timeout: float = 1.2):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 1200ms)
        """
        self.base_url = settings.account_validation_url
        self.timeout = timeout

    def get_eligible_accounts(
        self,
        customer_id: str,
        entity_id: str,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve eligible disbursement accounts for a customer.

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of account dictionaries with keys:
            - account_id: Account identifier
            - account_number: Masked account number
            - account_type: Account type (e.g., CHECKING, SAVINGS)
            - is_operable: Whether account can receive disbursement
            - operability_reason: Reason code if not operable
            - balance: Current balance (if available)

        Raises:
            TimeoutError: If request exceeds timeout budget
            ValueError: If API returns error
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/accounts/eligible",
                    params={"customer_id": customer_id, "entity_id": entity_id},
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return data.get("accounts", [])

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Account validation timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Account validation error: {e.response.status_code}"
            ) from e

    def validate_account_operability(
        self,
        account_id: str,
        customer_id: str,
        entity_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate specific account operability for disbursement.

        Args:
            account_id: Account identifier to validate
            customer_id: Customer identifier
            entity_id: Entity identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Operability result with keys:
            - account_id: Account identifier
            - is_operable: Boolean operability status
            - blocking_rules: List of blocking rule codes (if not operable)
            - reason: Human-readable reason
            - validated_at: Validation timestamp
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        payload = {
            "account_id": account_id,
            "customer_id": customer_id,
            "entity_id": entity_id
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/accounts/validate",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "account_id": account_id,
                    "is_operable": data.get("is_operable", False),
                    "blocking_rules": data.get("blocking_rules", []),
                    "reason": data.get("reason", ""),
                    "validated_at": data.get("validated_at")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Account validation timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Account validation error: {e.response.status_code}"
            ) from e

    def normalize_account_list(
        self,
        raw_accounts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize account list response for service layer.

        Args:
            raw_accounts: Raw account data from validation service

        Returns:
            Normalized account list with standardized fields
        """
        normalized = []

        for account in raw_accounts:
            normalized_account = {
                "account_id": account.get("account_id"),
                "account_number": account.get("account_number", "****"),
                "account_type": account.get("account_type", "UNKNOWN"),
                "is_operable": bool(account.get("is_operable", False)),
                "operability_reason": account.get("operability_reason"),
                "balance": account.get("balance")
            }

            # Add warning badge for low balance
            if normalized_account.get("balance") is not None:
                if normalized_account["balance"] < 0:
                    normalized_account["warning"] = "NEGATIVE_BALANCE"

            normalized.append(normalized_account)

        return normalized
