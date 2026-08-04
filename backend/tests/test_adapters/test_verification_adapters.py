"""Tests for Verification Adapters (Creditworthiness, Fraud, AML)"""
from unittest.mock import MagicMock, patch

import pytest

from app.adapters.aml_adapter import AMLAdapter
from app.adapters.creditworthiness_adapter import CreditworthinessAdapter
from app.adapters.fraud_adapter import FraudAdapter


@pytest.fixture
def creditworthiness_adapter():
    """Create creditworthiness adapter instance"""
    return CreditworthinessAdapter(timeout=2.5)


@pytest.fixture
def fraud_adapter():
    """Create fraud adapter instance"""
    return FraudAdapter(timeout=2.5)


@pytest.fixture
def aml_adapter():
    """Create AML adapter instance"""
    return AMLAdapter(timeout=2.5)


# Creditworthiness Adapter Tests

def test_creditworthiness_verify_pass(creditworthiness_adapter):
    """Test creditworthiness verification with PASS decision"""
    mock_response = {
        "decision": "APPROVED",
        "score": 750,
        "rating": "A",
        "provider_reference": "REF_123"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = creditworthiness_adapter.verify_creditworthiness(
            "customer_123", "entity_001", 10000.0, 48
        )

        assert result["decision"] == "PASS"
        assert result["score"] == 750
        assert result["rating"] == "A"


def test_creditworthiness_verify_reject(creditworthiness_adapter):
    """Test creditworthiness verification with REJECT decision"""
    mock_response = {
        "decision": "DECLINED",
        "score": 450,
        "rating": "D",
        "reason_code": "LOW_SCORE",
        "provider_reference": "REF_456"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = creditworthiness_adapter.verify_creditworthiness(
            "customer_123", "entity_001", 10000.0, 48
        )

        assert result["decision"] == "REJECT"
        assert result["reason_code"] == "LOW_SCORE"


def test_creditworthiness_normalize_decision(creditworthiness_adapter):
    """Test decision normalization"""
    assert creditworthiness_adapter._normalize_decision("APPROVED") == "PASS"
    assert creditworthiness_adapter._normalize_decision("ACCEPT") == "PASS"
    assert creditworthiness_adapter._normalize_decision("DECLINED") == "REJECT"
    assert creditworthiness_adapter._normalize_decision("DENIED") == "REJECT"
    assert creditworthiness_adapter._normalize_decision("MANUAL") == "REVIEW"
    assert creditworthiness_adapter._normalize_decision("UNKNOWN") == "REVIEW"


# Fraud Adapter Tests

def test_fraud_screen_pass(fraud_adapter):
    """Test fraud screening with PASS decision"""
    mock_response = {
        "risk_score": 0.15,
        "verdict": "LOW_RISK",
        "provider_reference": "FRAUD_123"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = fraud_adapter.screen_fraud_risk(
            "customer_123", "entity_001", 10000.0, "journey_789"
        )

        assert result["decision"] == "PASS"
        assert result["risk_score"] == 0.15
        assert result["verdict"] == "LOW_RISK"


def test_fraud_screen_reject(fraud_adapter):
    """Test fraud screening with REJECT decision"""
    mock_response = {
        "risk_score": 0.85,
        "verdict": "HIGH_RISK",
        "reason_code": "SUSPICIOUS_PATTERN",
        "provider_reference": "FRAUD_456"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = fraud_adapter.screen_fraud_risk(
            "customer_123", "entity_001", 10000.0, "journey_789"
        )

        assert result["decision"] == "REJECT"
        assert result["reason_code"] == "SUSPICIOUS_PATTERN"


def test_fraud_normalize_decision_by_score(fraud_adapter):
    """Test fraud decision normalization by score"""
    assert fraud_adapter._normalize_decision(0.2, None) == "PASS"
    assert fraud_adapter._normalize_decision(0.5, None) == "REVIEW"
    assert fraud_adapter._normalize_decision(0.8, None) == "REJECT"


def test_fraud_normalize_decision_by_verdict(fraud_adapter):
    """Test fraud decision normalization by verdict"""
    assert fraud_adapter._normalize_decision(None, "LOW_RISK") == "PASS"
    assert fraud_adapter._normalize_decision(None, "MEDIUM_RISK") == "REVIEW"
    assert fraud_adapter._normalize_decision(None, "HIGH_RISK") == "REJECT"


# AML Adapter Tests

def test_aml_screen_pass(aml_adapter):
    """Test AML screening with PASS decision"""
    mock_response = {
        "pep_match": False,
        "sanctions_match": False,
        "provider_reference": "AML_123"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = aml_adapter.screen_aml_pbc("customer_123", "entity_001")

        assert result["decision"] == "PASS"
        assert result["pep_match"] is False
        assert result["sanctions_match"] is False


def test_aml_screen_review_pep(aml_adapter):
    """Test AML screening with PEP match (REVIEW)"""
    mock_response = {
        "pep_match": True,
        "sanctions_match": False,
        "reason_code": "PEP_MATCH",
        "provider_reference": "AML_456"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = aml_adapter.screen_aml_pbc("customer_123", "entity_001")

        assert result["decision"] == "REVIEW"
        assert result["pep_match"] is True


def test_aml_screen_reject_sanctions(aml_adapter):
    """Test AML screening with sanctions match (REJECT)"""
    mock_response = {
        "pep_match": False,
        "sanctions_match": True,
        "reason_code": "SANCTIONS_MATCH",
        "provider_reference": "AML_789"
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        mock_client.return_value.__enter__.return_value.post.return_value.raise_for_status = lambda: None

        result = aml_adapter.screen_aml_pbc("customer_123", "entity_001")

        assert result["decision"] == "REJECT"
        assert result["sanctions_match"] is True


def test_aml_normalize_decision(aml_adapter):
    """Test AML decision normalization"""
    assert aml_adapter._normalize_decision(False, False) == "PASS"
    assert aml_adapter._normalize_decision(True, False) == "REVIEW"
    assert aml_adapter._normalize_decision(False, True) == "REJECT"
    assert aml_adapter._normalize_decision(True, True) == "REJECT"
