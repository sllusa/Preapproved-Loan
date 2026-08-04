"""Document generation and acknowledgement routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.common import ErrorResponse
from app.schemas.documents import (
    DocumentAcknowledgementRequest,
    DocumentPackageResponse,
    DocumentResponse,
)
from app.services.document_service import DocumentService
from app.services.journey_orchestrator import JourneyOrchestrator

router = APIRouter(tags=["documents"])


@router.post(
    "/api/v1/preapproved-loans/journeys/{journey_id}/documents/generate",
    response_model=DocumentPackageResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
def generate_document_package(
    journey_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate legal document package (SECCI/INE) for the journey.

    Resolves legal package variant from entity configuration.
    """
    try:
        document_service = DocumentService(db)

        package = document_service.generate_document_package(
            journey_id=journey_id,
            customer_id=current_user["customer_id"],
            entity_id=current_user["entity_id"]
        )

        # Mock documents for response
        mock_documents = [
            DocumentResponse(
                document_id=f"{package.package_id}_secci",
                document_type="SECCI",
                document_url=f"/api/v1/documents/{package.package_id}/secci.pdf",
                generated_at=package.generated_at
            ),
            DocumentResponse(
                document_id=f"{package.package_id}_contract",
                document_type="CONTRATO",
                document_url=f"/api/v1/documents/{package.package_id}/contract.pdf",
                generated_at=package.generated_at
            )
        ]

        return DocumentPackageResponse(
            package_id=package.package_id,
            journey_id=package.journey_id,
            legal_package_mode=package.legal_package_mode,
            documents=mock_documents,
            generated_at=package.generated_at
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
    "/api/v1/preapproved-loans/journeys/{journey_id}/documents/acknowledge",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Package Not Found"}
    }
)
def acknowledge_documents(
    journey_id: str,
    request: DocumentAcknowledgementRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Capture customer acknowledgement of document review.

    Creates immutable audit evidence and advances journey state.
    """
    try:
        document_service = DocumentService(db)
        journey_orchestrator = JourneyOrchestrator(db)

        # Get package
        package = document_service.get_document_package(request.package_id)
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Document package not found", "status_code": 404, "retryable": False}
            )

        if not request.acknowledged:
            raise ValueError("Customer must acknowledge documents to proceed")

        # Capture acknowledgement
        _acknowledgement = document_service.capture_acknowledgement(
            package_id=request.package_id,
            journey_id=package.journey_id,
            customer_id=current_user["customer_id"],
            acknowledged_document_ids=request.acknowledged_documents
        )

        # Advance journey state to pending signature
        journey = journey_orchestrator.apply_transition(
            journey_id=package.journey_id,
            target_state="PENDIENTE_FIRMA",
            trigger="DOCUMENTS_ACKNOWLEDGED",
            actor_type="CUSTOMER"
        )

        return {
            "journey_id": package.journey_id,
            "state": journey.current_state,
            "acknowledgement_recorded": True,
            "message": "Documents acknowledged, proceed to signature"
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
