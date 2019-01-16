import oauth2
import types
import requests
from utils import error

class ReceiptsClient:
    def __init__(self):
        self._api_client = oauth2.OAuth2Client()
        self._api_client_ready = False

    def do_auth(self):
        print("Starting OAuth2 flow...")
        self._api_client.start_auth()

        print("OAuth2 flow completed, testing...")
        response = client.test_api_call()
        if "authenticated" in response:
            print("Test successful!")
        else:
            error("OAuth2 flow seems to have failed.")
        self._api_client_ready = True
    
    def load_transactions(self):
        if self._api_client is None || not self._api_client_ready:
            error("API client not initialised.")

        

    
            
        
    