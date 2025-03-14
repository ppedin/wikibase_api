"""
This file contains functionalities to call the external Wikibase API. 
!!! The execution of operation via the Wikibase REST API (used here) is subject to rate limits.
Special rate limits should be applied to the users (to see later). !!!
"""

import requests

#  Wikibase API Client. A client is created every time the API is called. The client is associated with everything that is required to communicate with the Wikibase API.  
class WikibaseAPIClient():
    def __init__(self, username, password, base_url="https://wikibase.netseven.work"):
        self.base_url = base_url
        self.username = username
        self.password = password

    def check_connection(self, check_endpoint="/rest.php/wikibase/v1/entities/properties/P1"):
        #  Checks if the connection with the client has success. If not, the error is propagated to the endpoint logic and an error is raised. 
        #  The endpoint used to check if the connection is established has been chosen randomly. 

        response = requests.get(self.base_url + check_endpoint, auth=(self.username, self.password))
        if response.status_code == 200:
            return True
        else:
            return False

    def retrieve_item_by_label(self, item_label, label_language):
        #  Uses the Mediawiki API to search an item by its label. 
        #  The Wikibase API has recently introduced this feature, but it is not yet recommended for production.
        #  Returns True if the item has been found, None otherwise. 
        params = {
            "action": "wbsearchentities",
            "search": item_label,
            "language": label_language,
            "type": "item",
            "format": "json"
        }
        response = requests.get(self.base_url + "/api.php", auth=(self.username, self.password), params=params)
        if response.status_code == 200:
            #  The response is a dictionary with the key search whose value is a list of all the retrieved items. 
            if len(response.json()["search"]) > 0:
                #  This means that an item with that label has been found. 
                #  We also return the id of the item if the item has been found. 
                #  We chose to return only the first item since we assume that, if the instance has been managed correctly, 
                #  only one item should exist with the given label.
                return True, response.json()["search"][0]["id"]
            else:
                return False, None
        else:
            raise Exception("Error searching for the existence of the item by label: " + response.status_code)


    def add_item(self, label, label_language, description=None, description_language=None):
        #  Add an item to the WB instance, with a given label and a given language, and eventually a description. 
        #  Uses the payload for the entities/items endpoint of the original Wikibase REST API. 
        #  Returns the id of the added item if the adding request succeeds, otherwise it returns the None. 

        self.payload = {
                "item": {
                    "labels": {label_language: label},
                    "descriptions": {description_language: description} if description else {},
                    "aliases": {},
                    "statements": {},
                    "sitelinks": {}
                },
                "comment": ""
            }

        response = requests.post(self.base_url + "/rest.php/wikibase/v1/entities/items", auth=(self.username, self.password), json=self.payload)

        if response.status_code == 201:
            return response.json()["id"]

        return None


    def retrieve_property_info(self, property_id):

        response = requests.get(self.base_url + "/rest.php/wikibase/v1/entities/properties/" + property_id, auth=(self.username, self.password))

        if response.status_code == 200:
            return response.json()

        return None

    
    def add_statement(self, item_id, property_id, value, statement_addition_type):
        #  Uses the payload for statements endpoint of the original Wikibase REST API.
        #  So far, it assumes no qualifiers or references are added.
        #  TODO: evaluate if references and qualifiers will be used and how, so to add them.

        payload = {
            "statement": {
                "property": {
                    "id": property_id
                },
                "value": {
                    "type": statement_addition_type,  
                    "content": value
                },
                "qualifiers": [],
                "references": []
            },
            "tags": [],
            "bot": False,
            "comment": "",
        }

        response = requests.post(self.base_url + "/rest.php/wikibase/v1/entities/items/" + item_id + "/statements", auth=(self.username, self.password), json=payload)

        if response.status_code == 201:
            return True
        print(response.status_code)
        print(response.text)
        return None


    def add_property(self, label, label_language, description, description_language, data_type="string"):
        #  This method will not be used by the actual API, but it serves to tweak the properties of the instance in order to adapt the expected datatypes. 
        #  TODO: change the datatypes of the properties (so far, it has only been done for the Title property).

        payload = {
                "property": {
                    "data_type": "string",
                    "labels": {label_language: label},
                    "descriptions": {description_language: description},
                    "aliases": {},
                    "statements": {}
                },
                "comment": ""
            }

        response = requests.post(self.base_url + "/rest.php/wikibase/v1/entities/properties", auth=(self.username, self.password), json=payload)

        if response.status_code == 201:
            return response.json()["id"]
        print(response.status_code)
        print(response.text)

        return None


    


if __name__ == "__main__":
    import time
    client = WikibaseAPIClient("wikibase", "zf4mcfAS5cE3")
    print(client.check_connection())
    """
    client.add_property("Licence", "en", "Information about a licence or other legal agreement applicable to the resource", "en", "string")
    time.sleep(5)
    client.add_property("Volume", "en", "The volume number or the tome number of the resource", "en", "string")
    time.sleep(5)
    client.add_property("Total pages", "en", "The total number of pages", "en", "string")
    time.sleep(5)
    client.add_property("Format", "en", "The format of the resource (refers to the physical sheet size of the resource, such as 8°, 12°) ", "en", "string")
    time.sleep(5)
    client.add_property("Total documents", "en", "The total number of documents contained in the resource", "en", "string")
    time.sleep(5)
    client.add_property("Digital archive name", "en", "Information about the repository where the digital material is stored", "en", "string")
    time.sleep(5)
    client.add_property("Print archive name", "en", "Information about the repository where the printed material is stored", "en", "string")
    time.sleep(5)
    client.add_property("Digital archive code", "en", "The archival code associated with the digital resource", "en", "external-id")
    time.sleep(5)
    client.add_property("Print archive code", "en", "The archival code associated with the print resource", "en", "external-id")
    time.sleep(5)
    client.add_property("Digital archive URL", "en", "A hyperlink to additional resources or information related to the repository or the materials in question", "en", "url")
    time.sleep(5)
    client.add_property("Encoding text", "en", "Information about the presence or the absence of the text encoding", "en", "string")
    time.sleep(5)
    client.add_property("Text recording", "en", "A prose description of the rationale and methods used in selecting texts, or parts of a text, for inclusion in the resource", "en", "string")
    time.sleep(5)
    client.add_property("Language", "en", "A single language or sublanguage used within the resource", "en", "string")
    time.sleep(5)
    client.add_property("Abstract", "en", "A summary or formal abstract added by the encoder", "en", "string")
    time.sleep(5)
    client.add_property("Keyword", "en", "A single-word, multi-word, or phrase identifying the topic or nature of the resource", "en", "string")
    time.sleep(5)
    client.add_property("Revision changes", "en", "The date of the revision/A brief description of the object of the revision", "en", "string")
    """

    #  client.add_item("Title", "it", "The title of the digital resource (e.g. The War of the Roses, The Prayer for the Wounded)", "it")
