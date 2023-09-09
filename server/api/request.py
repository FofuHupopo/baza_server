import requests

from dadata import Dadata
from pprint import pprint

from api.utils import sort_by_similarity


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
        "calculate": "https://api.cdek.ru/v2/calculator/tarif",
        "order": "https://api.cdek.ru/v2/order"
    }
    HEADERS = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
    }
