"""Document Generation Adapter - Legal package generation"""
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class DocumentAdapter:
    """
    Adapter for Document Generation Service integration.

    Handles:
    - SECCI/INE document package generation
    - Template-based legal text rendering
    - Document metadata retrieval
    """

    def __init__(self, timeout: float = 3.0):
        """
        Initialize adapter with timeout budget.

        Args:
            timeout: Request timeout in seconds (LLD: 3000ms)
        """
        self.base_url = settings.document_generation_url
        self.timeout = timeout

    def generate_document_package(
        self,
        customer_id: str,
        entity_id: str,
        journey_id: str,
        amount: float,
        term_months: int,
        tin: float,
        tae: float,
        installment: float,
        total_cost: float,
        legal_package_mode: str,
        language: str = "es",
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate legal document package (SECCI or INE).

        Args:
            customer_id: Customer identifier
            entity_id: Entity identifier
            journey_id: Journey identifier
            amount: Loan amount
            term_months: Loan term in months
            tin: Nominal interest rate
            tae: APR
            installment: Monthly installment
            total_cost: Total cost of credit
            legal_package_mode: SECCI or INE
            language: Document language (default: es)
            correlation_id: Optional correlation ID for tracing

        Returns:
            Document package with keys:
            - package_id: Generated package identifier
            - documents: List of document objects
            - mode: SECCI or INE
            - language: Document language
            - generated_at: Generation timestamp

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
            "loan_parameters": {
                "amount": amount,
                "term_months": term_months,
                "tin": tin,
                "tae": tae,
                "installment": installment,
                "total_cost": total_cost
            },
            "legal_package_mode": legal_package_mode,
            "language": language
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/documents/generate",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return {
                    "package_id": data.get("package_id"),
                    "documents": data.get("documents", []),
                    "mode": legal_package_mode,
                    "language": language,
                    "generated_at": data.get("generated_at")
                }

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Document generation timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Document generation error: {e.response.status_code}"
            ) from e

    def get_document_url(
        self,
        document_id: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Get download URL for a generated document.

        Args:
            document_id: Document identifier
            correlation_id: Optional correlation ID for tracing

        Returns:
            Download URL for the document
        """
        headers = {}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/documents/{document_id}/url",
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()
                return data.get("url", "")

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Document URL retrieval timeout after {self.timeout}s"
            ) from e
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Document URL retrieval error: {e.response.status_code}"
            ) from e

    def normalize_document_list(
        self,
        raw_documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize document list for service layer.

        Args:
            raw_documents: Raw document data from generation service

        Returns:
            Normalized document list with standardized fields
        """
        normalized = []

        for doc in raw_documents:
            normalized_doc = {
                "document_id": doc.get("document_id"),
                "document_type": doc.get("document_type", "UNKNOWN"),
                "document_name": doc.get("document_name", "Untitled"),
                "content_type": doc.get("content_type", "application/pdf"),
                "size_bytes": doc.get("size_bytes", 0),
                "download_url": doc.get("download_url"),
                "requires_acknowledgement": doc.get("requires_acknowledgement", True)
            }

            normalized.append(normalized_doc)

        return normalized
