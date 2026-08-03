"""Tests for SCA Signature Adapter"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.sca_adapter import SCAAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return SCAAdapter(timeout=5.0)


def test_initiate_signature_success(adapter):
    """Test successful signature initiation"""
    mock_response = {
        "session_id": "sig_123",
        "redirect_url": "https://sca-provider.example.com/sign?session=sig_123",
        "expires_at": "2026-08-03T10:15:00Z"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = adapter.initiate_signature(
            customer_id="customer_123",
            entity_id="entity_001",
            journey_id="journey_789",
            contract_digest="digest_abc",
            callback_url="https://api.example.com/callback"
        )

        assert result["session_id"] == "sig_123"
        assert "redirect_url" in result
        assert result["status"] == "INITIATED"


def test_initiate_signature_timeout(adapter):
    """Test signature initiation timeout"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.initiate_signature(
                customer_id="customer_123",
                entity_id="entity_001",
                journey_id="journey_789",
                contract_digest="digest_abc",
                callback_url="https://api.example.com/callback"
            )

        assert "SCA signature initiation timeout" in str(exc_info.value)


def test_verify_signature_success(adapter):
    """Test signature verification with SUCCESS status"""
    mock_response = {
        "status": "SUCCESS",
        "provider_reference": "PROV_REF_123",
        "completed_at": "2026-08-03T10:10:00Z"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status = lambda: None

        result = adapter.verify_signature("sig_123")

        assert result["status"] == "SUCCESS"
        assert result["provider_reference"] == "PROV_REF_123"


def test_verify_signature_not_found(adapter):
    """Test signature verification for not found session"""
    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock(status_code=404)
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )

        result = adapter.verify_signature("sig_123")

        assert result["status"] == "NOT_FOUND"


def test_normalize_callback_status(adapter):
    """Test callback status normalization"""
    assert adapter.normalize_callback_status("SUCCESS") == "SUCCESS"
    assert adapter.normalize_callback_status("COMPLETED") == "SUCCESS"
    assert adapter.normalize_callback_status("SIGNED") == "SUCCESS"
    assert adapter.normalize_callback_status("FAILED") == "FAILED"
    assert adapter.normalize_callback_status("ERROR") == "FAILED"
    assert adapter.normalize_callback_status("CANCELLED") == "CANCELLED"
    assert adapter.normalize_callback_status("USER_CANCELLED") == "CANCELLED"
    assert adapter.normalize_callback_status("EXPIRED") == "EXPIRED"
    assert adapter.normalize_callback_status("TIMEOUT") == "EXPIRED"
    assert adapter.normalize_callback_status("UNKNOWN") == "FAILED"
