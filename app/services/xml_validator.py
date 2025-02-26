"""
XML Validator Service for Scheda bibliografica

This module provides validation services for XML content against 
the Scheda bibliografica schema.
"""
from typing import Dict, List, Tuple, Optional, Any
import xml.etree.ElementTree as ET
import re
from app.services.validation_results import ValidationResult, ValidationError


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field_id: Optional[str], message: str, path: str = ""):
        self.field_id = field_id
        self.message = message
        self.path = path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            "field_id": self.field_id,
            "message": self.message,
            "path": self.path
        }


class ValidationResult:
    """Represents the result of a validation."""
    
    def __init__(self, valid: bool, errors: List[ValidationError] = None):
        self.valid = valid
        self.errors = errors or []
    
    def add_error(self, error: ValidationError) -> None:
        """Add an error to the validation result."""
        self.errors.append(error)
        self.valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary representation."""
        return {
            "valid": self.valid,
            "errors": [error.to_dict() for error in self.errors]
        }


class XMLValidator:
    """
    This validator class only checks that a byte content of an XML file has correct XML syntax.
    This is a preliminary check: detailed check about the presence of the mandatory fields will be performed by the SchemaValidator objects. 
    """

    def __init__(self) -> None:
        pass

    def validate(self, content: bytes) -> ValidationResult:
        try:
            ET.fromstring(content)  #  Tries to parse the bytes of the file. 
            return ValidationResult(valid=True)  
        except ET.ParseError as e:
            return ValidationResult(valid=False, errors=[ValidationError(None, str(e))])


def get_xml_validator() -> XMLValidator:
    """Get the singleton instance of the XML validator."""
    return XMLValidator()