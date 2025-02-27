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

        



if __name__ == "__main__":
    client = WikibaseAPIClient("wikibase", "zf4mcfAS5cE3")
    print(client.check_connection())
    label = "ABCSU"
    print(client.retrieve_item_by_label(label, "it"))