"""Common schemas used across multiple endpoints"""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format"""
    detail: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")
    retryable: bool = Field(False, description="Whether the client should retry")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Pagination wrapper for list endpoints"""
    items: List[T] = Field(..., description="List of items in current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")

    @property
    def pages(self) -> int:
        """Total number of pages"""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Whether there is a next page"""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Whether there is a previous page"""
        return self.page > 1
