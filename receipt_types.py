import json
from copy import deepcopy

# Implements Receipts API data types.

class Type:
    def marshal(self):
        return json.dumps(self.data)

class SubItem(Type):
    def __init__(self, description, quantity, unit, amount, currency, tax):
        self.data = {
            "description": description,
            "quantity": quantity,
            "unit": unit,
            "amount": amount,
            "currency": currency,
            "tax": tax,
        }

class Item(Type):
    def __init__(self, description, quantity, unit, amount, currency, tax, sub_items):
        self.data = {
            "description": description,
            "quantity": quantity,
            "unit": unit,
            "amount": amount,
            "currency": currency,
            "tax": tax,
            "sub_items": sub_items,
        }

class Payment(Type):
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

class Tax(Type):
    def __init__(self, description, amount, currency, tax_number):
        self.data = {
            "description": description,
            "amount": amount,
            "currency": currency,
            "tax_number": tax_number,
        }

class Merchant(Type):
    def __init__(self, name, online, phone, email, store_name, store_address, store_postcode):
        self.data = {
            "name": name,
            "online": online,
            "phone": phone,
            "email": email,
            "store_name": store_name,
            "store_address": store_address,
            "store_postcode": store_postcode,
        }


class Receipt(Type):
    def __init__(self, id, external_id, transaction_id, total, currency, merchant, payments, taxes, items):
        self.data = {
            "id": id, 
            "external_id": external_id,
            "transaction_id": transaction_id,
            "total": total,
            "currency": currency,
            "merchant": merchant,
            "payments": payments,
            "taxes": taxes,
            "items": items,
        }


    
