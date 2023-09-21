import requests
import threading

from pathlib import Path
from dadata import Dadata
from pprint import pprint

from .utils import sort_by_similarity


class AddressSearch:
    TOKEN = "48ab36191d6ef5b11a3ae58d406b7d641a1fbd32"
    DADATA = Dadata(TOKEN)
    VALID_SEARCH_FIELDS = [
        "city", "street", "house"
    ]
    
    def search(raw: str, search_field: str, limit: int=None) -> list[str]:
        if search_field.lower() not in AddressSearch.VALID_SEARCH_FIELDS:
            return []            

        result = AddressSearch.DADATA.suggest("address", raw)

        if not result:
            return []

        response = list(filter(lambda x: "/" not in x, {
            value
            for res in result
            if (value := res.get("data", {}).get(search_field, ""))
        }))
                    
        response = sort_by_similarity(raw, response)

        if limit:
            response = response[:limit]

        return response


class SendMessage:
    TOKEN = "7d411796-32ff-4222-aa0b-980fa320a25f"
    URL = "https://api.imobis.ru/v3/message/sendSMS"
    
    @staticmethod
    def send(phone: str, code: str):
        result = requests.post(
            url=SendMessage.URL,
            json={
                "sender": "baza-store",
                "phone": phone,
                "text": f"Ваш код авторизации: {code}",
                "ttl": 300,
            },
            headers={
                "Authorization": f"Token {SendMessage.TOKEN}",
                "Content-Type": "application/json"
            }
        )
        
        return result.status_code == 200
        

class Delivery:
    URLS = {
        "calculate": "https://api.cdek.ru/v2/calculator/tarifflist",
        "order": "https://api.cdek.ru/v2/order",
        "auth": "https://api.cdek.ru/v2/oauth/token"
    }
    AUTH = {
        "account": "gHMHkeStBTHiIlwgJdMEAPAUL6i7iKZC",
        "secure": "rQcSMwlrUHXykRSdBZaE0fVxBMa2gKdO"
    }
    HEADERS = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
    }
    TOKEN = {
        "Authorization": ""
    }
    TARIFF_CODES = {
        "address": [482],
        "stock": [483, 486]
    }
    
    @classmethod
    def get_header(cls):
        cls.HEADERS.update(cls.TOKEN)
        return cls.HEADERS

    @classmethod
    def _request(cls, url: str, json: dict) -> dict:
        r = requests.post(Delivery.URLS[url], headers=cls.get_header(), json=json)
        
        if r.status_code == 401:
            r = requests.post(
                Delivery.URLS["auth"],
                headers=cls.get_header(),
                params={
                    "grant_type": "client_credentials",
                    "client_id": Delivery.AUTH["account"],
                    "client_secret": Delivery.AUTH["secure"]
                }
            )
            
            cls.TOKEN["Authorization"] = f'Bearer {r.json().get("access_token", "")}'
            
            r = requests.post(Delivery.URLS[url], headers=cls.get_header(), json=json)

        return r.json()

    @staticmethod
    def calculate_address(address: str, weight: int):
        return Delivery._calculate(
            {
                "address": address
            },
            "address", weight
        )

    @staticmethod
    def calculate_stock(cdek_code: int, weight: int):
        return Delivery._calculate(
            {
                "code": cdek_code
            },
            "stock", weight
        )

    @staticmethod
    def _calculate(to_location: dict, tariff_filter: str, weight: int):
        r = Delivery._request("calculate", json={
            "from_location": {
                "postal_code": 460053,
            },
            "to_location": to_location,
            "packages": [
                {
                    "weight": weight,
                    "height": 23,
                    "length": 19,
                    "width": 10,
                }
            ],
        })

        result = list(filter(
            lambda tariff: tariff["tariff_code"] in Delivery.TARIFF_CODES[tariff_filter],
            r["tariff_codes"]
        ))[0]

        return {
            "price": result["delivery_sum"],
            "period_min": result["period_min"],
            "period_max": result["period_max"],
        }



class Synchronizer:
    BASE_URL = "http://127.0.0.1:5000/update/"
    URLS = {
        "quantity": BASE_URL + "quantity"
    }
    
    @staticmethod
    def _request(url: str, body: dict) -> None:
        r = requests.post(
            Synchronizer.URLS[url],
            json=body
        )
    
    @staticmethod
    def _streaming_request(url: str, body: dict):
        stream_request = threading.Thread(
            target=Synchronizer._request,
            args=(url, body)
        )
        stream_request.start()
    
    @staticmethod
    def quantity_update(modification_id: str, quantity: int):
        Synchronizer._streaming_request(
            "quantity",
            {
                "quantity": quantity,
                "modification_id": modification_id
            }
        )


if __name__ == "__main__":
    # pprint(Delivery.calculate_address("Москва, Севастопольский проспект, 43"))
    Synchronizer.quantity_update("123", 10)
