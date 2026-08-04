"""Tests for Pre-Approval Engine Adapter"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.pre_approval_adapter import PreApprovalAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return PreApprovalAdapter(timeout=1.5)


def test_get_offers_success(adapter):
    """Test successful offer retrieval"""
    mock_response = {
        "offers": [
            {
                "offer_id": "offer_123",
                "max_amount": 15000.0,
                "max_term_months": 60,
                "indicative_tin": 6.5,
                "indicative_tae": 6.72,
                "validity_ends_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "status": "ACTIVE"
            }
        ]
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )

        offers = adapter.get_offers("customer_123", "entity_001")

        assert len(offers) == 1
        assert offers[0]["offer_id"] == "offer_123"
        assert offers[0]["max_amount"] == 15000.0


def test_get_offers_timeout(adapter):
    """Test timeout handling"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.get_offers("customer_123", "entity_001")

        assert "Pre-Approval Engine timeout" in str(exc_info.value)


def test_check_offer_status_success(adapter):
    """Test offer status check"""
    mock_response = {
        "offer_id": "offer_123",
        "status": "ACTIVE",
        "validity_ends_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )

        status = adapter.check_offer_status("offer_123")

        assert status["offer_id"] == "offer_123"
        assert status["status"] == "ACTIVE"


def test_normalize_offer_actionable(adapter):
    """Test offer normalization for actionable offer"""
    raw_offer = {
        "offer_id": "offer_123",
        "max_amount": 15000.0,
        "max_term_months": 60,
        "indicative_tin": 6.5,
        "indicative_tae": 6.72,
        "validity_ends_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "status": "ACTIVE"
    }

    normalized = adapter.normalize_offer(raw_offer, entity_min_amount=5000.0)

    assert normalized["actionable"] is True
    assert normalized["max_amount"] == 15000.0


def test_normalize_offer_below_minimum(adapter):
    """Test offer normalization for below minimum"""
    raw_offer = {
        "offer_id": "offer_123",
        "max_amount": 3000.0,
        "max_term_months": 60,
        "indicative_tin": 6.5,
        "indicative_tae": 6.72,
        "validity_ends_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "status": "ACTIVE"
    }

    normalized = adapter.normalize_offer(raw_offer, entity_min_amount=5000.0)

    assert normalized["actionable"] is False
    assert normalized["reason"] == "BELOW_ENTITY_MINIMUM"


def test_normalize_offer_expired(adapter):
    """Test offer normalization for expired offer"""
    raw_offer = {
        "offer_id": "offer_123",
        "max_amount": 15000.0,
        "max_term_months": 60,
        "indicative_tin": 6.5,
        "indicative_tae": 6.72,
        "validity_ends_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "status": "ACTIVE"
    }

    normalized = adapter.normalize_offer(raw_offer, entity_min_amount=5000.0)

    assert normalized["actionable"] is False
    assert normalized["reason"] == "EXPIRED"
