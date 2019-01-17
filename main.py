import json
import uuid

import requests

import config
import oauth2
import receipt_types
from utils import error

class ReceiptsClient:
    ''' An example single-account client of the Monzo Transaction Receipts API. 
        For the underlying OAuth2 implementation, see oauth2.OAuth2Client.
    '''

    def __init__(self):
        self._api_client = oauth2.OAuth2Client()
        self._api_client_ready = False
        self._account_id = None
        self.transactions = []


    def do_auth(self):
        ''' Perform OAuth2 flow mostly on command-line and retrieve information of the
            authorised user's current account information, rather than from joint account, 
            if present.
        '''

        print("Starting OAuth2 flow...")
        self._api_client.start_auth()

        print("OAuth2 flow completed, testing API call...")
        response = self._api_client.test_api_call()
        if "authenticated" in response:
            print("API call test successful!")
        else:
            error("OAuth2 flow seems to have failed.")
        self._api_client_ready = True

        print("Retrieving account information...")
        success, response = self._api_client.api_get("accounts", {})
        if not success or "accounts" not in response or len(response["accounts"]) < 1:
            error("Could not retrieve accounts information")
        
        # We will be operating on personal account only.
        for account in response["accounts"]:
            if "type" in account and account["type"] == "uk_retail":
                self._account_id = account["id"]
                print("Retrieved account information.")
                return

        if self._account_id is None:
            error("Could not find a personal account")
    

    def list_transactions(self):
        ''' An example call to the end point documented in
            https://docs.monzo.com/#list-transactions, other requests 
            can be implemented in a similar fashion. 
        '''
        if self._api_client is None or not self._api_client_ready:
            error("API client not initialised.")

        # Our call is not paginated here with e.g. "limit": 10, which will be slow for
        # accounts with a lot of transactions.
        success, response = self._api_client.api_get("transactions", {
            "account_id": self._account_id,
        })

        if not success or "transactions" not in response:
            error("Could not list past transactions ({})".format(response))
        
        self.transactions = response["transactions"]
        print("All transactions loaded.")
        

    def read_receipt(self, receipt_id):
        ''' Retrieve receipt for a transaction with an external ID of our choosing.
        '''
        success, response = self._api_client.api_get("transaction-receipts", {
            "external_id": receipt_id,
        })
        if not success:
            error("Failed to load receipt: {}".format(response))
        
        print("Receipt read: {}".format(response))

    
    def example_add_receipt_data(self):
        ''' An example in which we add receipt data to the latest transaction 
            of the account, with fabricated information. You can set varying 
            receipts data on the same transaction again and again to test it 
            if you need to. 
        '''
        if len(self.transactions) == 0:
            error("No transactions found, either it was not loaded with list_transactions() or there's no transaction in the Monzo account :/")

        most_recent_transaction = self.transactions[-1]
        print("Using most recent transaction to attach receipt: {}".format(most_recent_transaction))

        # Using a random receipt ID we generate as external ID
        receipt_id = uuid.uuid4().hex
        
        # Price amounts are in the number of pences.
        example_sub_item_1 = receipt_types.SubItem("Bananas loose", 1.5, "kg", 119, "GBP", 0)
        example_sub_item_2 = receipt_types.SubItem("Organic bananas", 1, "kg", 150, "GBP", 0)
        example_items = [receipt_types.Item("Selected bananas", 2.5, "kg", 269, "GBP", 0, [example_sub_item_1,
            example_sub_item_2])]
        if abs(most_recent_transaction["amount"]) > 269:
            example_items.append(receipt_types.Item("Excess fare", 1, "", abs(most_recent_transaction["amount"]) 
            - 269, "GBP", 20, []))
        example_payments = [receipt_types.Payment("card", "123321", "1234", "A10B2C", "", "", "", "", 
            abs(most_recent_transaction["amount"]), "GBP")]
        example_taxes = [receipt_types.Tax("VAT", 0, "GBP", "12345678")]
        
        example_receipt = receipt_types.Receipt("", receipt_id, most_recent_transaction["id"], 
            abs(most_recent_transaction["amount"]), "GBP", example_payments, example_taxes, example_items)
        example_receipt_marshaled = example_receipt.marshal()
        print("Uploading receipt data to API: ", json.dumps(example_receipt_marshaled, indent=4, sort_keys=True))
        print("")
        
        success, response = self._api_client.api_put("transaction-receipts/", example_receipt_marshaled)
        if not success:
            error("Failed to upload receipt: {}".format(response))

        print("Successfully uploaded receipt {}: {}".format(receipt_id, response))
        return receipt_id

    
    def example_register_webhook(self, incoming_endpoint):
        '''
        This is an example on registering a webhook with Monzo for Monzo's server to call your own
        backend service endpoint when certain events happen on an account. This is useful if you 
        deploy an API client as a backend service with an incoming interface exposed to the internet.
        Your backend code can then, for example, attach receipts to new transactions in an event-
        driven manner. For more details, see https://docs.monzo.com/#webhooks
        '''

        print("Listing webhooks on account")
        success, response = self._api_client.api_get("webhooks", {
            "account_id": self._account_id,
        })
        if not success:
            error("Failed to list webhooks: {}".format(response))
        print("Existing webhooks: ", response)

        print("Registering a webhook with callback URL {} ...".format(incoming_endpoint))
        success, response = self._api_client.api_post("webhooks", {
            "account_id": self._account_id,
            "url": incoming_endpoint,
        })
        if not success or "webhook" not in response:
            error("Failed to register webhook: {}".format(response))
        print("Successfully registered webhooks ", response)

        return response["webhook"]["id"]
        

if __name__ == "__main__":
    client = ReceiptsClient()
    client.do_auth()
    client.list_transactions()
    receipt_id = client.example_add_receipt_data()
    client.read_receipt(receipt_id)
    client.example_register_webhook("https://example.com/webhook_callback") 
    # The webhook endpoint used should be an HTTP-style server served by your own app server.

    
    
            
        
    