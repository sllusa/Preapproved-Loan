"""Tests for Document Generation Adapter"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.document_adapter import DocumentAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return DocumentAdapter(timeout=3.0)


def test_generate_document_package_success(adapter):
    """Test successful document package generation"""
    mock_response = {
        "package_id": "pkg_123",
        "documents": [
            {
                "document_id": "doc_001",
                "document_type": "SECCI",
                "document_name": "SECCI Document",
                "content_type": "application/pdf",
                "size_bytes": 102400,
                "download_url": "https://docs.example.com/doc_001.pdf",
                "requires_acknowledgement": True
            }
        ],
        "generated_at": "2026-08-03T10:00:00Z"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = adapter.generate_document_package(
            customer_id="customer_123",
            entity_id="entity_001",
            journey_id="journey_789",
            amount=10000.0,
            term_months=48,
            tin=6.5,
            tae=6.72,
            installment=234.85,
            total_cost=11272.80,
            legal_package_mode="SECCI"
        )

        assert result["package_id"] == "pkg_123"
        assert len(result["documents"]) == 1
        assert result["mode"] == "SECCI"


def test_generate_document_package_timeout(adapter):
    """Test document generation timeout"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.generate_document_package(
                customer_id="customer_123",
                entity_id="entity_001",
                journey_id="journey_789",
                amount=10000.0,
                term_months=48,
                tin=6.5,
                tae=6.72,
                installment=234.85,
                total_cost=11272.80,
                legal_package_mode="SECCI"
            )

        assert "Document generation timeout" in str(exc_info.value)


def test_get_document_url_success(adapter):
    """Test successful document URL retrieval"""
    mock_response = {
        "url": "https://docs.example.com/doc_001.pdf"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status = lambda: None

        url = adapter.get_document_url("doc_001")

        assert url == "https://docs.example.com/doc_001.pdf"


def test_normalize_document_list(adapter):
    """Test document list normalization"""
    raw_documents = [
        {
            "document_id": "doc_001",
            "document_type": "SECCI",
            "document_name": "SECCI Document",
            "content_type": "application/pdf",
            "size_bytes": 102400,
            "download_url": "https://docs.example.com/doc_001.pdf",
            "requires_acknowledgement": True
        },
        {
            "document_id": "doc_002",
            "document_type": "CONTRACT",
            "document_name": "Loan Contract"
        }
    ]

    normalized = adapter.normalize_document_list(raw_documents)

    assert len(normalized) == 2
    assert normalized[0]["document_id"] == "doc_001"
    assert normalized[0]["requires_acknowledgement"] is True
    assert normalized[1]["document_type"] == "CONTRACT"
    assert normalized[1]["size_bytes"] == 0  # Default
