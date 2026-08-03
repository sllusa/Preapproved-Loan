"""Schemas for document endpoints"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Individual document in a package"""
    document_id: str = Field(..., description="Document identifier")
    document_type: str = Field(..., description="Document type: SECCI, INE, CONTRATO")
    document_url: str = Field(..., description="Document download URL")
    generated_at: datetime = Field(..., description="Document generation timestamp")


class DocumentPackageResponse(BaseModel):
    """Document package response"""
    package_id: str = Field(..., description="Package identifier")
    journey_id: str = Field(..., description="Journey identifier")
    legal_package_mode: str = Field(..., description="Legal mode: SECCI, INE")
    documents: List[DocumentResponse] = Field(..., description="Documents in package")
    generated_at: datetime = Field(..., description="Package generation timestamp")

    class Config:
        from_attributes = True


class DocumentAcknowledgementRequest(BaseModel):
    """Acknowledge document review and acceptance"""
    package_id: str = Field(..., description="Package identifier")
    acknowledged: bool = Field(..., description="Whether customer acknowledges documents")
    acknowledged_documents: List[str] = Field(..., description="List of acknowledged document IDs")
