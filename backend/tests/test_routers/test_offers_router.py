"""Tests for offers router"""
from datetime import datetime, timedelta


def test_list_offers_returns_offers_list(client, mock_entity_config):
    """Test GET /api/v1/preapproved-loans/offers returns offers list"""
    response = client.get("/api/v1/preapproved-loans/offers")

    assert response.status_code == 200
    data = response.json()

    assert "offers" in data
    assert "total" in data
    assert isinstance(data["offers"], list)
    assert data["total"] >= 0


def test_list_offers_validates_entity_config(client):
    """Test that list_offers validates entity configuration exists"""
    # Without entity config, should fail
    response = client.get("/api/v1/preapproved-loans/offers")

    # Should return 400 or 500 depending on error handling
    assert response.status_code in [400, 500]


# Note: Individual offer GET endpoint does not exist in the API
# Offers are retrieved as a list only via GET /api/v1/preapproved-loans/offers
