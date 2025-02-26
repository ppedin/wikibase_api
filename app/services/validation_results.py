from typing import Dict, List, Optional, Any


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