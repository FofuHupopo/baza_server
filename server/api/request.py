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