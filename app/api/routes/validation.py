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
import app.services.detectors as detectors
import app.services.callers as callers
import app.schemas.error as errors


#  List all the detectors. This will be used to detect the fields inside a xml file. 
#  Detectors are associated with the index of the property in the Wikibase instance, since it seems that there is no other way to access all the properties of the instance by label. 
#  A possibility could require making the Wikidata Query Service accessible on our instance, but this is something we could investigate in the future. 
#  For the moment, we leave it like that, even if this solution is not recommended since it assumes that the properties are stable in the instance. 
#  TODO: Complete this mapping when all the detectors will be defined.
detectors = {
    "P72": detectors.TitleDetector(),
}

#  TODO: of course, this will be removed in the last version since they will be passed. 
DEFAULT_WIKIBASE_USERNAME = "wikibase"
DEFAULT_WIKIBASE_PASSWORD = "zf4mcfAS5cE3"


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
    label: str = Form(...),  #  label of the item that will be passed to the instance. 
    file: UploadFile = File(...),  
    resource_type: str = Form(...),
    username: str = Form(DEFAULT_WIKIBASE_USERNAME),  #TODO: remove the default value in the final version
    password: str = Form(DEFAULT_WIKIBASE_PASSWORD),  #TODO: remove the default value in the final version
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
            #  Creates a Wikibase client and checks if the connection can be established.
            client = callers.WikibaseAPIClient(username, password)
            if not client.check_connection():
                raise HTTPException(status_code=500, detail="Connection to the Wikibase instance failed")
            
            #  First, it checks if an item with the given label already exists in the Wikibase instance.
            #  If the item already exists, it triggers an early response.  
            #  We assume that all the items that are added to the instance have an Italian label. 
            #  TODO: if we want to add items in another language, we will need to pass the label language explicitly in the request. 
            item_exists, item_id = client.retrieve_item_by_label(label, label_language="it")
            if item_exists:
                return HTTPException(status_code=400, detail=f"Item with the given label already exists (item {item_id}). Use the patch endpoint if you want to add/change properties. ")
            #  The item with the given label is added to the WB instance. 
            #  The add_item method also allows to add a description for the item (we must specify the language of the description).
            #  TODO: if we want to add a description when creating an item, we should pass the description explicitly in the request. 
            item_id = client.add_item(label, label_language="it")
            #  add_item returns the id of the added item if addition takes place successfully, otherwise it returns None
            if item_id is None:
                raise HTTPException(status_code=500, detail="Item addition failed")
            
            #  Identification of the fields present in the xml file.
            #  This is done by applying all the detectors. 
            for field in detectors.keys():
                #  detection_results is a list with all the values detected for the field.
                detection_results = detectors[field].detect(content)
                #  For every detected value, a statement is added to WB. 
                for detection_result in detection_results:
                    #  A value is just a string of text. 
                    pass
                    #  Addition of the statement. It is True if addition happened successfully, None otherwise
                    #  So far, we assume that qualifiers and references are not used. 
                    outcome_statement_addition = client.add_statement(item_id, field, detection_result)
                    if not outcome_statement_addition:
                        raise HTTPException(status_code=500, detail="Statement addition failed")
                    
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





