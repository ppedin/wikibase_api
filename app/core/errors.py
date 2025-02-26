"""
Custom error classes for the application.

This module defines custom error classes that can be raised
throughout the application and handled appropriately.
"""
from typing import Any, Dict, Optional


class BaseAPIError(Exception):
    """Base class for API errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "error",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIError):
    """Error raised when validation fails."""
    
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            details=details
        )


class SchemaNotFoundError(BaseAPIError):
    """Error raised when a schema is not found."""
    
    def __init__(
        self,
        resource_type: str,
        message: Optional[str] = None
    ):
        message = message or f"Schema not found for resource type: {resource_type}"
        super().__init__(
            message=message,
            code="schema_not_found",
            status_code=404,
            details={"resource_type": resource_type}
        )


class XMLParseError(BaseAPIError):
    """Error raised when XML parsing fails."""
    
    def __init__(
        self,
        message: str = "Failed to parse XML",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="xml_parse_error",
            status_code=400,
            details=details
        )