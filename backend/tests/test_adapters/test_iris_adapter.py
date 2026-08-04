"""Tests for IRIS Adapter"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.iris_adapter import IRISAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return IRISAdapter(booking_timeout=4.0, status_timeout=2.0)


def test_book_loan_confirmed(adapter):
    """Test successful booking with immediate confirmation"""
    mock_response = {
        "iris_reference": "IRIS_ABC123",
        "status": "CONFIRMED"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )

        result = adapter.book_loan(
            idempotency_key="key_123",
            customer_id="customer_123",
            entity_id="entity_001",
            amount=10000.0,
            term_months=48,
            disbursement_account_id="account_456",
            contract_reference="contract_789"
        )

        assert result["status"] == "CONFIRMED"
        assert result["iris_reference"] == "IRIS_ABC123"


def test_book_loan_pending(adapter):
    """Test booking with pending status"""
    mock_response = {
        "iris_reference": "IRIS_ABC123"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=202,
            json=lambda: mock_response
        )

        result = adapter.book_loan(
            idempotency_key="key_123",
            customer_id="customer_123",
            entity_id="entity_001",
            amount=10000.0,
            term_months=48,
            disbursement_account_id="account_456",
            contract_reference="contract_789"
        )

        assert result["status"] == "PENDING"
        assert result["iris_reference"] == "IRIS_ABC123"


def test_book_loan_failed(adapter):
    """Test booking failure"""
    mock_response = {
        "error_code": "INSUFFICIENT_FUNDS",
        "message": "Insufficient funds"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=400,
            json=lambda: mock_response,
            text="error"
        )

        result = adapter.book_loan(
            idempotency_key="key_123",
            customer_id="customer_123",
            entity_id="entity_001",
            amount=10000.0,
            term_months=48,
            disbursement_account_id="account_456",
            contract_reference="contract_789"
        )

        assert result["status"] == "FAILED"
        assert result["error_code"] == "INSUFFICIENT_FUNDS"


def test_book_loan_timeout(adapter):
    """Test booking timeout handling"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.book_loan(
                idempotency_key="key_123",
                customer_id="customer_123",
                entity_id="entity_001",
                amount=10000.0,
                term_months=48,
                disbursement_account_id="account_456",
                contract_reference="contract_789"
            )

        assert "requires reconciliation" in str(exc_info.value)


def test_get_booking_status_success(adapter):
    """Test successful status retrieval"""
    mock_response = {
        "status": "CONFIRMED",
        "disbursement_status": "COMPLETED"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status = lambda: None

        result = adapter.get_booking_status("IRIS_ABC123")

        assert result["status"] == "CONFIRMED"
        assert result["disbursement_status"] == "COMPLETED"


def test_get_booking_status_not_found(adapter):
    """Test status retrieval for not found booking"""
    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock(status_code=404)
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )

        result = adapter.get_booking_status("IRIS_ABC123")

        assert result["status"] == "UNKNOWN"
        assert "not found" in result["message"].lower()


def test_submit_disbursement_success(adapter):
    """Test successful disbursement submission"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            text="success"
        )

        result = adapter.submit_disbursement("IRIS_ABC123", "account_456")

        assert result["status"] == "SUBMITTED"
