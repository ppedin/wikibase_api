"""
This file contains functionalities to call the external Wikibase API. 
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
            "comment": ""
        }

        response = requests.post(self.base_url + "/rest.php/wikibase/v1/entities/items/" + item_id + "/statements", auth=(self.username, self.password), json=payload)

        if response.status_code == 201:
            return True
        print(response.status_code)
        print(response.text)
        return None


    def add_property(self, label, label_language, description, description_language):
        #  This method will not be used by the actual API, but its serve to tweak the properties of the instance in order to adapt the expected datatypes. 
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
    client = WikibaseAPIClient("wikibase", "zf4mcfAS5cE3")
    print(client.check_connection())
    #  client.add_property("Edition", "en", "The edition of the digital resource (e.g. first, second, third, ...)/The edition of the print resource (e.g. first, second, third, ...)", "en")
    client.add_item("Title", "it", "The title of the digital resource (e.g. The War of the Roses, The Prayer for the Wounded)", "it")
