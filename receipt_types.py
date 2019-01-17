import json

# Implements the payload protocol for Transaction Receipts API. 
# See example_add_receipt_data() in main.py for data types example usage.

class SubItem:
    def __init__(self, description, quantity, unit, amount, currency, tax):
        self.data = {
            "description": description,
            "quantity": quantity,
            "unit": unit,
            "amount": amount,
            "currency": currency,
            "tax": tax,
        }

class Item:
    def __init__(self, description, quantity, unit, amount, currency, tax, sub_items):
        self.data = {
            "description": description,
            "quantity": quantity,
            "unit": unit,
            "amount": amount,
            "currency": currency,
            "tax": tax,
            "sub_items": [sub.data for sub in sub_items],
        }

class Payment:
    def __init__(self, type, bin, last_four, auth_code, aid, mid, tid, gift_card_type, amount, currency):
        self.data = {
            "type": type,
            "bin": bin,
            "last_four": last_four,
            "auth_code": auth_code,
            "aid": aid,
            "mid": mid,
            "tid": tid,
            "gift_card_type": gift_card_type,
            "amount": amount,
            "currency": currency,
        }

class Tax:
    def __init__(self, description, amount, currency, tax_number):
        self.data = {
            "description": description,
            "amount": amount,
            "currency": currency,
            "tax_number": tax_number,
        }

class Receipt:
    def __init__(self, id, external_id, transaction_id, total, currency, payments, taxes, items):
        self.data = {
            "id": id, 
            "external_id": external_id,
            "transaction_id": transaction_id,
            "total": total,
            "currency": currency,
            "payments": [payment.data for payment in payments],
            "taxes": [tax.data for tax in taxes],
            "items": [item.data for item in items],
        }
    
    def marshal(self):
        return json.dumps(self.data)


    
