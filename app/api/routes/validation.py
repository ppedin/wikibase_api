"""
Validation API Routes

This module defines the API routes for validating XML content
against the Scheda bibliografica schema.
"""
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.xml_validator import get_xml_validator, ValidationResult, ValidationError, XMLValidator
from app.services.schema_registry import SchemaValidator, get_schema_validator

# Router definition (using the FastAPI class APIRouter).
#  The tag serves to organize the related endpoints in the API documentation
# Every endpoint in that router will have the /validation prefix in its URL.
router = APIRouter(prefix="/validation", tags=["validation"])

#  Pydantic classes
class ErrorResponse(BaseModel):
    """Model for validation error responses."""
    field_id: Optional[str] = None
    message: str
    path: str = ""


class ValidationResponse(BaseModel):
    """Model for validation responses."""
    valid: bool
    errors: List[ErrorResponse] = []


#  Definition of the validation endpoint.
#  The endpoint returns a ValidationResponse object (Pydantic ensures the response has the ValidationResponse structure)
#  The logic for the endpoint is an asynchronous function
@router.post("/", response_model=ValidationResponse)
async def validate_xml(
    file: UploadFile = File(...),  
    resource_type: str = Form(...),
    xml_validator: XMLValidator = Depends(get_xml_validator),
): 
    try:

        schema_validator = get_schema_validator(resource_type)
        # Reads the file using the UploadFile class method read()
        content = await file.read()

        # Uses the XMLValidator. All the validation logic is defined in the XMLValidator. 
        xml_validation_result = xml_validator.validate(content)  #  xml_validation_result is an instance of ValidationResult.
        #  The class has an attribute valid which is True when the content is valid. Then it has an errors field where the exceptions have been captured and saved in case of errors. 

        if not xml_validation_result.valid:  #  The file is not a correct xml. 
            return ValidationResponse(
                valid=False,
                errors=[
                    ErrorResponse(
                        field_id=None,
                        message=error.message,  #  The exception which has been captured is described here. 
                        path=error.path
                    )
                    for error in xml_validation_result.errors
                ]
            )

        #  If the file is valid xml, the SchemaValidator is applied to check it has all the mandatory fields. 
        schema_validation_result = schema_validator.validate(content)

        if not schema_validation_result.valid:
            return ValidationResponse(
                valid=False,
                errors=[
                    ErrorResponse(
                        field_id=None,
                        message=error.message,  
                        path=error.path
                    )
                    for error in schema_validation_result.errors
                ]
            )

        else:
            return ValidationResponse(
                valid=True,
                errors=[]
            )




    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/schemas", response_model=List[str])
async def list_schemas(validator: XMLValidator = Depends(get_xml_validator)):
    """
    List all available schema types.
    
    Args:
        validator: The XML validator service.
        
    Returns:
        A list of available schema types.
    """
    return validator.schema_registry.list_schemas()