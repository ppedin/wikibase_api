"""
Error schemas for the API.

This module defines the Pydantic models for error responses.
"""
from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field_id: Optional[str] = None
    message: str
    path: str = ""


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    valid: bool = False
    errors: List[ErrorDetail] = []


class HTTPError(BaseModel):
    """HTTP error response."""
    detail: str

    