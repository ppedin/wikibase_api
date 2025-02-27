"""
This module defines validation schemas for each resource type.
While the xml validator in xml_validator.py checks if the file has an xml syntax, the validation schemas
check for the presence of mandatory elements. 
"""
from typing import Dict, List, Optional, Union, Any
import xml.etree.ElementTree as ET  #  We will use this library to check if mandatory metadata are present in the file
import json
import app.services.detectors as detectors
from app.services.validation_results  import ValidationResult, ValidationError


#  Here we define the validation schema for every resource type.
#  A validation schema is defined via Detector objects (defined in detectors.py). 
#  A detector object corresponds to a field in the file provided by Links and checks whether the field is detected according to the patterns specified in the file. 

#  TODO: Complete this mapping when mandatory attributes for new resource types will be defined!
detectors_per_resource_type = {
    'scheda_bibliografica': [
        detectors.TitleDetector(),
        #  detectors.AuthorDetector(),
        #  detectors.DigitalFormatDetector()
    ]
}

#  !! Each SchemaValidator has associated one or more objects of type Detector (one for each mandatory field). 
#  These objects are used to check if the file contains the required metadata.
class SchemaValidator:
    #  General class for Schema validators. 
    def __init__(self, resource_type: str) -> None:
        self.detectors = detectors_per_resource_type[resource_type]
    
    #  The validate method is common to all the SchemaValidator objects.
    #  It iterates over the list of detectors for that SchemaValidator and ensures every of them has success (since each of them corresponds to a mandatory attribute). 
    def validate(self, content: bytes) -> ValidationResult:
        for detector in self.detectors:
            detection_results = detector.detect(content)
            if len(detection_results) == 0:
                return ValidationResult(valid=False, errors=[ValidationError(None, "The field {} is mandatory and has not been detected in the xml provided.".format(detector.field))])
        return ValidationResult(valid=True)


#  This function will be used to dynamically genwerate a SchemaValidator object that will be generated dynamically in validate_xml
def get_schema_validator(resource_type: str) -> SchemaValidator:
    """Get the schema validator for a given resource type."""
    return SchemaValidator(resource_type)