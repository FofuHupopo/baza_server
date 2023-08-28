import requests
from dadata import Dadata
from pprint import pprint


class DadataAddressAutoComplete:
    TOKEN = "48ab36191d6ef5b11a3ae58d406b7d641a1fbd32"
    DADATA = Dadata(TOKEN)
    
    def search(search: str, limit=None):
        result = DadataAddressAutoComplete.DADATA.suggest("address", search)
        
        if not result:
            return None
        
        response = [
            res.get("value")
            for res in result
        ]
        
        if limit:
            response = response[:limit]
        
        return response
    
    def get(address: str):
        result = DadataAddressAutoComplete.DADATA.suggest("address", address)

        if not result:
            return None
        
        result = result[0]
        
        pprint(result)
        
        region = result.get("data", {}).get("region", "")
        region_type = result.get("data", {}).get("region_type_full", "")
        
        if region_type == "область":
            region = f"{region} {region_type}".capitalize()
        elif region_type == "республика":
            region = f"{region_type} {region}".title()
        elif region_type == "автономный округ":
            region = region.replace("Автономный округ", "АО")
            
        return {
            "address": result.get("value"),
            "city": result.get("data", {}).get("city"),
            "region": region,
            "lat": result.get("data", {}).get("geo_lat"),
            "lon": result.get("data", {}).get("geo_lon")
        }
        

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
