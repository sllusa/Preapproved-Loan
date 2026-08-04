"""Simulation calculation and confirmation routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.services.journey_orchestrator import JourneyOrchestrator
from app.services.simulation_service import SimulationService

router = APIRouter(tags=["simulations"])


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/simulation",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid simulation parameters"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def create_simulation(
    journey_id: str,
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate real-time simulation for requested amount and term.

    Validates amount and term against offer bounds, calculates installment, TIN, APR/TAE, and total cost.
    """
    try:
        from app.services.journey_orchestrator import JourneyOrchestrator

        journey_orchestrator = JourneyOrchestrator(db)
        simulation_service = SimulationService(db)

        # Get journey to obtain offer_id
        journey = journey_orchestrator.get_journey(journey_id)
        if not journey:
            raise ValueError(f"Journey {journey_id} not found")

        snapshot = simulation_service.calculate_simulation(
            offer_id=journey.offer_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"],
            requested_amount=request.amount,
            requested_term_months=request.term_months
        )

        return SimulationResponse(
            simulation_id=snapshot.simulation_id,
            offer_id=snapshot.offer_id,
            requested_amount=snapshot.requested_amount,
            requested_term_months=snapshot.requested_term_months,
            monthly_installment=snapshot.monthly_installment,
            applied_tin=snapshot.applied_tin,
            applied_tae=snapshot.applied_tae,
            total_cost=snapshot.total_cost,
            total_interest=snapshot.total_interest
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
    "/api/v1/preapproved-loans/journeys/{journey_id}/simulation/confirm",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Simulation Not Found"}
    }
)
def confirm_simulation(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm simulation and proceed to account selection.

    Advances journey state to PENDIENTE_INFORMACION_PRECONTRACTUAL.
    """
    try:
        _simulation_service = SimulationService(db)
        journey_orchestrator = JourneyOrchestrator(db)

        # Get journey
        journey = journey_orchestrator.get_journey(journey_id)
        if not journey:
            raise ValueError("Journey not found")

        # Get latest simulation for journey
        # Note: In production, this would fetch the most recent simulation for the journey
        # For now, we'll use a simplified approach

        # Advance state to next step
        journey = journey_orchestrator.apply_transition(
            journey_id=journey.journey_id,
            target_state="PENDIENTE_INFORMACION_PRECONTRACTUAL",
            trigger="SIMULATION_CONFIRMED",
            actor_type="CUSTOMER"
        )

        return {
            "journey_id": journey.journey_id,
            "state": journey.current_state,
            "next_action": "SELECT_ACCOUNT",
            "message": "Simulation confirmed, proceed to account selection"
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
