import requests
import sys, uuid
import base64
import urllib.parse as urllib
import json
from utils import error

# A very simple OAuth2 client for the Monzo Third Party API. You presently cannot use
# this API for public applications, as only a small amount of users you nominate can
# authorise your application to their Monzo account with this API. This API however
# grants access to more resource than the AISP API for regulated AISPs including receipts.

try:
    import config
except:
    print("Cannot import config, register your application on developers.monzo.com, \
copy config-example.py to config.py, and configure your client credentials.")
    sys.exit(1)

class OAuth2Client:
    ''' This auth flow implements the process of acquiring an access token from the
        Monzo Third Party Developer API, as described in 
        https://docs.monzo.com/#acquire-an-access-token
    '''
    
    def __init__(self):
        self._oauth_state = uuid.uuid4().hex
        # Cryptographically-secure randomised state protects the client browser 
        # from cross site forgery attacks, while we don't need it as a command
        # line application, we still send a randomised state nevertheless to 
        # demonstrate.
        self._is_confidential_client = config.MONZO_CLIENT_IS_CONFIDENTIAL
    
    def start_auth(self):
        ''' Builds a URL to be used to initiate OAuth2 flow on the OAuth Portal. '''
        oauth2_GET_params = {
            "client_id": config.MONZO_CLIENT_ID,
            "redirect_uri": config.MONZO_OAUTH_REDIRECT_URI,
            "response_type": config.MONZO_RESPONSE_TYPE,
            "state": self._oauth_state
        }
        request_url = "https://{}/?{}".format(config.MONZO_OAUTH_HOSTNAME,
            urllib.urlencode(oauth2_GET_params, doseq=True))
        print("Visit {} and follow email flow to obtain your temporary authorization code...".format(request_url))
        self.wait_for_auth_flow()
    

    def wait_for_auth_flow(self):
        ''' Parses the temporary authorization code returned from authenticating with Email login link. '''
        callback_url = input("Once done, paste your callback URL here: ").strip()
        try:
            callback = urllib.urlparse(callback_url).query
        except:
            error("cannot parse callback URL, try again.")

        callback_qs = dict(urllib.parse_qsl(callback)) # Annoyingly parse_qs() parses string values into dicts.
        if "code" not in callback_qs:
            error("cannot find temporary auth code in callback URL")
        if "state" not in callback_qs:
            error("cannot find randomised auth state in callback URL")
        if callback_qs["state"].strip() != self._oauth_state:
            error("invalid randomised auth state in callback URL, did you use the most recent login link?")
        
        self._auth_code = callback_qs["code"].strip()
        self.exchange_auth_code()
    
    
    def exchange_auth_code(self):
        '''Exchanges the temporary authorization code with an access token for a non-confidential application. '''
        if self._auth_code == "":
            error("no auth code, have you completed intial auth flow")

        oauth2_POST_params = {
            "grant_type": config.MONZO_AUTH_GRANT_TYPE,
            "client_id": config.MONZO_CLIENT_ID,
            "client_secret": config.MONZO_CLIENT_SECRET,
            "redirect_uri": config.MONZO_OAUTH_REDIRECT_URI,
            "code": self._auth_code,
        }
        request_url = "https://{}/oauth2/token?".format(config.MONZO_API_HOSTNAME)
        response = requests.post(request_url, data=oauth2_POST_params)
        if response.status_code != 200:
            error("Auth failed, bad status code returned: {} ({})".format(response.status_code,
                response.text))

        response_object = response.json()
        if "access_token" in response_object:
            print("Auth successful.") 
            self._access_token = response_object["access_token"]

            if "refresh_token" in response_object:
                self._refresh_token = response_object["refresh_token"]
            else:
                self._is_confidential_client = False
                if config.MONZO_CLIENT_IS_CONFIDENTIAL:
                    print("Warning: this client is not registered as confidential, we will not be able to refresh token")
    

    def refresh_access_token(self):
        ''' If we are a confidential client, we can refresh the access token to get a new one derived from the same OAuth
            authorisation. 
        '''
        if not self._is_confidential_client:
            error("Not a confidential client, cannot refresh access token.")

        oauth2_POST_params = {
            "grant_type": config.MONZO_REFRESH_GRANT_TYPE,
            "client_id": config.MONZO_CLIENT_ID,
            "client_secret": config.MONZO_CLIENT_SECRET,
            "refresh_token": self._refresh_token,
        }
        request_url = "https://{}/oauth2/token?".format(config.MONZO_API_HOSTNAME)
        response = requests.post(request_url, data=oauth2_POST_params)
        if response.status_code != 200:
            error("Token refreshed failed, bad status code returned: {} ({})".format(response.status_code,
                response.text))
        
        response_object = response.json()
        if "access_token" in response_object:
            self._access_token = response_object["access_token"]
        else:
            error("No access token returned in token refresh response")
        if "refresh_token" in response_object:
            self._refresh_token = response_object["refresh_token"]
        else:
            error("No refresh token returned in token refresh response")
        print("Token refreshed, new access token and refresh token recorded.")
    
        
    def test_api_call(self):
        ''' Use the access token to send a test API call to the Monzo API. '''
        response = requests.get("https://{}/ping/whoami".format(config.MONZO_API_HOSTNAME), 
            headers={"Authorization": "Bearer {}".format(self._access_token)})
        if response.status_code != 200:
            error("API test call failed, bad status code returned: {} ({})".format(response.status_code,
                response.text))
        
        print("API test call successful.")
        print(response.text)

if __name__ == "__main__":
    client = OAuth2Client()
    client.start_auth()
    client.test_api_call()
    client.refresh_access_token()
