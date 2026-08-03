"""Tests for Amortization Schedule Adapter"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.adapters.amortization_adapter import AmortizationAdapter


@pytest.fixture
def adapter():
    """Create adapter instance"""
    return AmortizationAdapter(timeout=2.0)


def test_generate_schedule_success(adapter):
    """Test successful schedule generation"""
    mock_response = {
        "schedule_id": "sched_123",
        "installments": [
            {
                "installment_number": 1,
                "due_date": "2026-09-03",
                "principal": 150.0,
                "interest": 50.0,
                "total_payment": 200.0,
                "remaining_balance": 9850.0
            }
        ],
        "total_interest": 2400.0,
        "total_cost": 12400.0
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = adapter.generate_schedule(
            loan_id="loan_789",
            amount=10000.0,
            term_months=60,
            tin=6.5
        )

        assert result["schedule_id"] == "sched_123"
        assert result["loan_id"] == "loan_789"
        assert len(result["installments"]) == 1
        assert result["total_interest"] == 2400.0


def test_generate_schedule_timeout(adapter):
    """Test schedule generation timeout"""
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TimeoutError) as exc_info:
            adapter.generate_schedule(
                loan_id="loan_789",
                amount=10000.0,
                term_months=60,
                tin=6.5
            )

        assert "Amortization schedule generation timeout" in str(exc_info.value)


def test_get_schedule_success(adapter):
    """Test successful schedule retrieval"""
    mock_response = {
        "schedule_id": "sched_123",
        "installments": [
            {
                "installment_number": 1,
                "due_date": "2026-09-03",
                "principal": 150.0,
                "interest": 50.0,
                "total_payment": 200.0,
                "remaining_balance": 9850.0
            }
        ],
        "total_interest": 2400.0,
        "total_cost": 12400.0
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value.raise_for_status = lambda: None

        result = adapter.get_schedule("loan_789")

        assert result["schedule_id"] == "sched_123"
        assert result["loan_id"] == "loan_789"
        assert len(result["installments"]) == 1


def test_get_schedule_not_found(adapter):
    """Test schedule retrieval for not found loan"""
    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock(status_code=404)
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )

        with pytest.raises(ValueError) as exc_info:
            adapter.get_schedule("loan_789")

        assert "Schedule not found" in str(exc_info.value)


def test_normalize_installments(adapter):
    """Test installment list normalization"""
    raw_installments = [
        {
            "installment_number": 1,
            "due_date": "2026-09-03",
            "principal": 150.0,
            "interest": 50.0,
            "total_payment": 200.0,
            "remaining_balance": 9850.0
        },
        {
            "installment_number": 2,
            "due_date": "2026-10-03",
            "principal": 152.0,
            "interest": 48.0,
            "total_payment": 200.0,
            "remaining_balance": 9698.0
        }
    ]

    normalized = adapter.normalize_installments(raw_installments)

    assert len(normalized) == 2
    assert normalized[0]["installment_number"] == 1
    assert normalized[0]["principal"] == 150.0
    assert normalized[1]["installment_number"] == 2
