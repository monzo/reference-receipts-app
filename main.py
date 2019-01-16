import oauth2
import receipt_types
import requests
from utils import error

import json
import uuid

class ReceiptsClient:

    def __init__(self):
        self._api_client = oauth2.OAuth2Client()
        self._api_client_ready = False
        self._account_id = None
        self.transactions = []


    def do_auth(self):
        ''' Perform OAuth2 flow mostly on command line and retrieve
            current account information.
        '''

        print("Starting OAuth2 flow...")
        self._api_client.start_auth()

        print("OAuth2 flow completed, testing...")
        response = self._api_client.test_api_call()
        if "authenticated" in response:
            print("Test successful!")
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
    

    def load_transactions(self):
        ''' An example call to the end point documented in
            https://docs.monzo.com/#list-transactions, other requests 
            can be implemented in a similar fashion. 
        '''
        if self._api_client is None or not self._api_client_ready:
            error("API client not initialised.")

        success, response = self._api_client.api_get("transactions", {
            "account_id": self._account_id,
        }) # Not paginated here with e.g. "limit": 10, which will be slow. 

        if not success or "transactions" not in response:
            error("Could not past transactions ({})".format(response))
        
        self.transactions = response["transactions"]
        print("All transactions loaded.")
        

    def read_receipt(self, receipt_id):
        ''' Retrieve receipt by an external ID we name for the transaction.
        '''
        success, response = self._api_client.api_get("transaction-receipts", {
            "external_id": receipt_id,
        })
        if not success:
            error("Failed to load receipt: {}".format(response))
        
        print("Receipt read: {}".format(response))

    
    def example_add_receipt_data(self):
        ''' An example in which we add receipt data to the latest transaction 
            of the account, with fake information. You can set data for different
            receipts on the same transaction again and again to test it if you 
            need to. 
        '''
        if len(self.transactions) == 0:
            error("No transactions found, either it was not loaded with load_transactions() or there's no transaction in the Monzo account :/")

        most_recent_transaction = self.transactions[-1]
        print("Using most recent transaction to attach receipt: {}".format(most_recent_transaction))

        # Using a random receipt ID we generate as external ID
        receipt_id = uuid.uuid4().hex
        
        # Price amounts are in the number of pences.
        example_sub_item_1 = receipt_types.SubItem("Bananas loose", 1.5, "kg", 119, "GBP", 0)
        example_sub_item_2 = receipt_types.SubItem("Organic bananas", 1, "kg", 150, "GBP", 0)
        example_items = [receipt_types.Item("Selected bananas", 2.5, "kg", 269, "GBP", 0, [example_sub_item_1, example_sub_item_2])]
        if abs(most_recent_transaction["amount"]) > 269:
            example_items.append(receipt_types.Item("Excess fare", 1, "", abs(most_recent_transaction["amount"]) - 269, "GBP", 20, []))
        example_payments = [receipt_types.Payment("card", "123321", "1234", "A10B2C", "", "", "", "", abs(most_recent_transaction["amount"]), "GBP")]
        example_taxes = [receipt_types.Tax("VAT", 0, "GBP", "12345678")]
        example_merchant = receipt_types.Merchant("Fruit store", False, "0200000001", "fruit@fruitstore.com", "Fruit Store King's Cross", "King's Cross St Pancras",
            "N1 9AL")
        
        example_receipt = receipt_types.Receipt("", receipt_id, most_recent_transaction["id"], abs(most_recent_transaction["amount"]), "GBP", example_merchant,
            example_payments, example_taxes, example_items)
        example_receipt_marshaled = example_receipt.marshal()
        print(json.dumps(example_receipt_marshaled, indent=4, sort_keys=True))
        
        success, response = self._api_client.api_put("transaction-receipts/", example_receipt_marshaled)
        if not success:
            error("Failed to upload receipt: {}".format(response))

        print("Successfully uploaded receipt {}: {}".format(receipt_id, response))
        return receipt_id


if __name__ == "__main__":
    client = ReceiptsClient()
    client.do_auth()
    client.load_transactions()
    receipt_id = client.example_add_receipt_data()
    client.read_receipt(receipt_id)
    
    
            
        
    