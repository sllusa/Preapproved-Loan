"""PSD2/SCA signature orchestration routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.signature import (
    SignatureCallbackRequest,
    SignatureSessionResponse,
)
from app.services.journey_orchestrator import JourneyOrchestrator
from app.services.signature_service import SignatureService

router = APIRouter(tags=["signature"])


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/signature/initiate",
    response_model=SignatureSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
def initiate_signature(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate PSD2/SCA signature session.

    Returns provider redirect URL and session details.
    """
    try:
        signature_service = SignatureService(db)

        # Default callback URL - in production this would come from config
        callback_url = "https://ruralvia.com/signature/callback"

        session = signature_service.initiate_signature_session(
            journey_id=journey_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"],
            callback_url=callback_url
        )

        return SignatureSessionResponse(
            session_id=session.session_id,
            journey_id=session.journey_id,
            provider_url=session.provider_url,
            expires_at=session.expires_at,
            status=session.status
        )

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


@router.post(
    "/api/v1/preapproved-loans/signature/callback",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Session Not Found"}
    }
)
def signature_callback(
    request: SignatureCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle signature callback from SCA provider.

    Updates session status and advances journey state on successful signature.
    """
    try:
        signature_service = SignatureService(db)
        journey_orchestrator = JourneyOrchestrator(db)

        # Get session
        session = signature_service.get_signature_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Signature session not found", "status_code": 404, "retryable": False}
            )

        # Handle signature completion
        if request.status == "COMPLETED" and request.signed_at:
            session = signature_service.complete_signature_session(
                session_id=request.session_id,
                signed_at=request.signed_at,
                provider_reference=request.provider_reference
            )

            # Advance journey state to signed
            journey = journey_orchestrator.apply_transition(
                journey_id=session.journey_id,
                target_state="FIRMADO",
                trigger="SIGNATURE_COMPLETED",
                actor_type="CUSTOMER"
            )

            return {
                "journey_id": session.journey_id,
                "state": journey.current_state,
                "signature_status": "COMPLETED",
                "message": "Signature completed, proceed to booking"
            }
        else:
            # Handle cancellation or failure
            session = signature_service.cancel_signature_session(
                session_id=request.session_id,
                reason=request.status
            )

            return {
                "journey_id": session.journey_id,
                "state": "PENDIENTE_FIRMA",
                "signature_status": request.status,
                "message": "Signature not completed"
            }

    except HTTPException:
        raise
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
