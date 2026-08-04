"""Tests for Account Validation Adapter"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.account_adapter import AccountAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return AccountAdapter(timeout=1.2)


def test_get_eligible_accounts_success(adapter):
    """Test successful account retrieval"""
    mock_response = {
        "accounts": [
            {
                "account_id": "account_123",
                "account_number": "****1234",
                "account_type": "CHECKING",
                "is_operable": True
            },
            {
                "account_id": "account_456",
                "account_number": "****5678",
                "account_type": "SAVINGS",
                "is_operable": False,
                "operability_reason": "BLOCKED"
            }
        ]
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status = lambda: None

        accounts = adapter.get_eligible_accounts("customer_123", "entity_001")

        assert len(accounts) == 2
        assert accounts[0]["account_id"] == "account_123"
        assert accounts[0]["is_operable"] is True
        assert accounts[1]["is_operable"] is False


def test_get_eligible_accounts_timeout(adapter):
    """Test timeout handling"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.get_eligible_accounts("customer_123", "entity_001")

        assert "Account validation timeout" in str(exc_info.value)


def test_validate_account_operability_success(adapter):
    """Test account operability validation"""
    mock_response = {
        "is_operable": True,
        "blocking_rules": [],
        "reason": "Account is operable",
        "validated_at": "2026-08-03T10:00:00Z"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = adapter.validate_account_operability(
            "account_123", "customer_123", "entity_001"
        )

        assert result["is_operable"] is True
        assert len(result["blocking_rules"]) == 0


def test_validate_account_operability_blocked(adapter):
    """Test blocked account validation"""
    mock_response = {
        "is_operable": False,
        "blocking_rules": ["FROZEN", "LEGAL_HOLD"],
        "reason": "Account has legal hold",
        "validated_at": "2026-08-03T10:00:00Z"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = adapter.validate_account_operability(
            "account_123", "customer_123", "entity_001"
        )

        assert result["is_operable"] is False
        assert "FROZEN" in result["blocking_rules"]
        assert "LEGAL_HOLD" in result["blocking_rules"]


def test_normalize_account_list(adapter):
    """Test account list normalization"""
    raw_accounts = [
        {
            "account_id": "account_123",
            "account_number": "****1234",
            "account_type": "CHECKING",
            "is_operable": True,
            "balance": 5000.0
        },
        {
            "account_id": "account_456",
            "account_number": "****5678",
            "account_type": "SAVINGS",
            "is_operable": False,
            "balance": -100.0
        }
    ]

    normalized = adapter.normalize_account_list(raw_accounts)

    assert len(normalized) == 2
    assert normalized[0]["account_id"] == "account_123"
    assert normalized[0]["is_operable"] is True
    assert "warning" not in normalized[0]
    assert normalized[1]["warning"] == "NEGATIVE_BALANCE"
