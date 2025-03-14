"""
Validation API Routes

This module defines the API routes for validating XML content
against the Scheda bibliografica schema.
"""

import time

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from lxml import etree  #  This is used to parse the XML file parsed as input. 
import re  #  This is used to extract the name space from an XML element tag, 


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
detector_mapping = {
    "P72": detectors.TitleDetector(),
    #  "P73": detectors.ShortTitleDetector(),
    #  "P74": detectors.AlternativeTitleDetector(),
    #  "P75": detectors.AuthorDetector(),   #  TODO: we should clarify the author situation: Since the value in the xml-TEI should be the label of another item in the WB instance. 
    #  "P76": detectors.VIAFDetector(),
    #  "P77": detectors.ISNIDetector(),
    #  "P79": detectors.RoleDetector(),
    #  "P80": detectors.TypeDetector(),  #  TODO: doesn't work
    #  "P81": detectors.NameDetector(),  #  TODO: doesn't work
    #  "P82": detectors.EditionDetector(),
    #  "P83": detectors.DigitalFormatDetector(),
    #  "P84": detectors.EditorDetector(),
    #  "P85": detectors.IDResourceDetector(),
    #  "P86": detectors.DOIDetector(),
    #  "P87": detectors.PublicationDateDetector(),
    #  "P88": detectors.PublicationPlaceDetector(),
    #  "P89": detectors.IssuingAuthorityDetector(),
    #  "P90": detectors.AvailableInDetector(),
    #  "P91": detectors.DataLinkedResourcesDetector(),
    #  "P92": detectors.EditorialDetector(),
    #  "P93": detectors.OriginalEditionDetector(),
    
    
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
        
        try:
            root = etree.fromstring(content)  #  Parsing of the XML file is done here to avoid replicating the logic in each detector.
            m = re.match(r'\{(.*)\}', root.tag)  #  Extraction of the namespace (this is done here to avoid logic replication in detectors.)
            ns = m.group(1) if m else None
            ns_map = {'ns': ns} if ns else {}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cannot parse the input XML file. Error: {e}")

        #  If the file is valid xml, the SchemaValidator is applied to check it has all the mandatory fields. 
        schema_validation_result = schema_validator.validate(root, ns, ns_map)

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
            try:
                root = etree.fromstring(content)  #  Parsing of the XML file is done here to avoid replicating the logic in each detector.
                m = re.match(r'\{(.*)\}', root.tag)  #  Extraction of the namespace (this is done here to avoid logic replication in detectors.)
                namespace = m.group(1) if m else None
                ns_map = {'ns': namespace} if namespace else {}
            except:
                raise HTTPException(status_code=500, detail="Cannot parse the input XML file")
            
            #  Identification of the fields present in the xml file.
            #  This is done by applying all the detectors. 
            #  TODO: add transaction mechanisms so that if something goes wrong, the newly created item is canceled from the instance. 
            #  Unfortunately, it seems like the WB instance does not provide an endpoint for item deletion, so we will need to check the action API. 
            for field in detector_mapping.keys():
                #  retrieves information about the property. In particular, we need the data_type since this will
                #  impact how we add statements for that property. 
                try:
                    property_data_type = client.retrieve_property_info(field)["data_type"]
                except:
                    raise HTTPException(status_code=500, detail="Cannot retrieve the datatype of the property")
                #  We decide on the value of the "type" field of statement addition based on the data type on the property.
                #  This is crucial to ensure that statement addition is successful.
                if property_data_type == "wikibase-item":
                    statement_addition_type = "wikibase-entityid"  #  This ensures the value of the statement is a reference to a Wikibase item
                else:
                    statement_addition_type = "value"  #  This seems to hold for all properties with datatype different than "wikibase-item"    
                
                detection_results = detector_mapping[field].detect(root, ns, ns_map)

                #  detection_results = []
                
                #  For every detected value, a statement is added to WB. 
                for detection_result in detection_results:
                    #  If the value of the property is a reference to another Wikibase item, we should make sure the item exists in the WBinstance.
                    #  Otherwise, we raise an error.
                    if property_data_type == "wikibase-item":
                        detection_result_item_exists, detection_result_item_id = client.retrieve_item_by_label(detection_result, "it")  #  we assume values are in Italian
                        if not detection_result_item_exists:
                            raise HTTPException(status_code=500, detail=f"An item with the value specified in the xml file for the property {field} does not exist in the WB instance.")
                        else:
                            outcome_statement_addition = client.add_statement(item_id, field, detection_result_item_id, statement_addition_type)
                    else:
                        outcome_statement_addition = client.add_statement(item_id, field, detection_result, statement_addition_type)
                    #  The addition of the statement is True if the statement has been added successfully. 
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





