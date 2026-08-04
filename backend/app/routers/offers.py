"""Offer retrieval and eligibility routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.offers import OfferResponse, OffersListResponse
from app.services.offer_service import OfferService

router = APIRouter(tags=["offers"])


@router.get(
    "/api/v1/preapproved-loans/offers",
    response_model=OffersListResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
def list_offers(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve actionable pre-approved offers for the authenticated customer.

    Returns list of offers with eligibility status, expiry, and terms.
    """
    try:
        offer_service = OfferService(db)

        customer_id = current_user["customer_id"]
        entity_id = current_user["entity_id"]

        offers_data = offer_service.retrieve_offers(customer_id, entity_id)

        offers = [
            OfferResponse(
                offer_id=offer["offer_id"],
                customer_id=customer_id,
                entity_id=entity_id,
                max_amount=offer["max_amount"],
                max_term_months=offer["max_term_months"],
                indicative_tin=offer["indicative_tin"],
                indicative_tae=offer["indicative_tae"],
                validity_ends_at=offer["validity_ends_at"],
                offer_status=offer["offer_status"],
                reason=offer.get("reason")
            )
            for offer in offers_data
        ]

        return OffersListResponse(offers=offers, total=len(offers))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": str(e), "status_code": 400, "retryable": False}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
