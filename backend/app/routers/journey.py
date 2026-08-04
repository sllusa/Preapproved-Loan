"""Journey orchestration and resume routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.journey import JourneyResponse, JourneyResumeResponse
from app.services.journey_orchestrator import JourneyOrchestrator

router = APIRouter(prefix="/journey", tags=["journey"])


@router.post(
    "/start",
    response_model=JourneyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
def start_journey(
    offer_id: str,
    channel: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new journey for an offer.

    Creates journey instance in OFERTA_VIGENTE state.
    """
    try:
        import uuid

        from app.services.offer_service import OfferService

        offer_service = OfferService(db)
        journey_orchestrator = JourneyOrchestrator(db)

        # Check for existing journey
        existing = offer_service.check_existing_journey(
            customer_id=current_user["customer_id"],
            offer_id=offer_id
        )

        if existing and not journey_orchestrator.is_terminal_state(existing.current_state):
            raise ValueError(f"Active journey already exists for this offer: {existing.journey_id}")

        # Create new journey
        journey_id = f"journey_{uuid.uuid4().hex[:16]}"
        journey = journey_orchestrator.create_journey(
            journey_id=journey_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"],
            offer_id=offer_id,
            channel=channel
        )

        return JourneyResponse(
            journey_id=journey.journey_id,
            customer_id=journey.customer_id,
            entity_id=journey.entity_id,
            offer_id=journey.offer_id,
            current_state=journey.current_state,
            channel_last_used=journey.channel_last_used,
            created_at=journey.created_at,
            updated_at=journey.updated_at,
            resume_deadline_at=journey.resume_deadline_at
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


@router.get(
    "/{journey_id}",
    response_model=JourneyResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Journey Not Found"}
    }
)
def get_journey(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve journey details.
    """
    try:
        journey_orchestrator = JourneyOrchestrator(db)
        journey = journey_orchestrator.get_journey(journey_id)

        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Journey not found", "status_code": 404, "retryable": False}
            )

        return JourneyResponse(
            journey_id=journey.journey_id,
            customer_id=journey.customer_id,
            entity_id=journey.entity_id,
            offer_id=journey.offer_id,
            current_state=journey.current_state,
            channel_last_used=journey.channel_last_used,
            created_at=journey.created_at,
            updated_at=journey.updated_at,
            resume_deadline_at=journey.resume_deadline_at
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )


@router.get(
    "/{journey_id}/resume",
    response_model=JourneyResumeResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Journey Not Found"}
    }
)
def check_journey_resume(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if journey can be resumed and determine next step.

    Validates offer status and returns resumable state.
    """
    try:
        from app.services.offer_service import OfferService

        journey_orchestrator = JourneyOrchestrator(db)
        offer_service = OfferService(db)

        journey = journey_orchestrator.get_journey(journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Journey not found", "status_code": 404, "retryable": False}
            )

        # Check if journey is in terminal state
        if journey_orchestrator.is_terminal_state(journey.current_state):
            return JourneyResumeResponse(
                journey=JourneyResponse(
                    journey_id=journey.journey_id,
                    customer_id=journey.customer_id,
                    entity_id=journey.entity_id,
                    offer_id=journey.offer_id,
                    current_state=journey.current_state,
                    channel_last_used=journey.channel_last_used,
                    created_at=journey.created_at,
                    updated_at=journey.updated_at,
                    resume_deadline_at=journey.resume_deadline_at
                ),
                can_resume=False,
                next_step="TERMINAL_STATE",
                reason=f"Journey is in terminal state: {journey.current_state}"
            )

        # Revalidate offer
        offer_validation = offer_service.revalidate_offer(journey.offer_id)
        if not offer_validation.get("valid"):
            return JourneyResumeResponse(
                journey=JourneyResponse(
                    journey_id=journey.journey_id,
                    customer_id=journey.customer_id,
                    entity_id=journey.entity_id,
                    offer_id=journey.offer_id,
                    current_state=journey.current_state,
                    channel_last_used=journey.channel_last_used,
                    created_at=journey.created_at,
                    updated_at=journey.updated_at,
                    resume_deadline_at=journey.resume_deadline_at
                ),
                can_resume=False,
                next_step="OFFER_INVALID",
                reason=offer_validation.get("reason", "Offer is no longer valid")
            )

        # Determine next step based on current state
        next_step_map = {
            "OFERTA_VIGENTE": "START_SIMULATION",
            "EN_SIMULACION": "CONTINUE_SIMULATION",
            "PENDIENTE_INFORMACION_PRECONTRACTUAL": "SELECT_ACCOUNT",
            "PENDIENTE_VERIFICACIONES": "WAIT_VERIFICATIONS",
            "PENDIENTE_FIRMA": "COMPLETE_SIGNATURE",
            "FIRMADO": "EXECUTE_BOOKING",
            "ABONADO": "VIEW_ACTIVATION"
        }

        next_step = next_step_map.get(journey.current_state, "UNKNOWN")

        return JourneyResumeResponse(
            journey=JourneyResponse(
                journey_id=journey.journey_id,
                customer_id=journey.customer_id,
                entity_id=journey.entity_id,
                offer_id=journey.offer_id,
                current_state=journey.current_state,
                channel_last_used=journey.channel_last_used,
                created_at=journey.created_at,
                updated_at=journey.updated_at,
                resume_deadline_at=journey.resume_deadline_at
            ),
            can_resume=True,
            next_step=next_step,
            reason=None
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "status_code": 500, "retryable": True}
        )
