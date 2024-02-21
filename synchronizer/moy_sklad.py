import requests


class MoySklad:
    MOYSKLAD_TOKEN = "9ad7b79af08525d5313361e63b77f8439cd185f7"
    HEADERS = {
        "Authorization": f"Bearer {MOYSKLAD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    }
    MOYSKLAD_URLS = {
        "PRODUCTS": "https://online.moysklad.ru/api/remap/1.2/entity/product?filter=archived=false",
        "PRODUCT_DETAIL": "https://online.moysklad.ru/api/remap/1.2/entity/product/{}",
        "MODIFICATIONS": "https://online.moysklad.ru/api/remap/1.2/entity/variant?filter=productid={}",
        "MODIFICATION_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/variant/{}/images",
        "PRODUCT_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/product/{}/images",
        "ASSORTMENT": "https://online.moysklad.ru/api/remap/1.2/entity/assortment?filter=id={}",
        "DOWNLOAD": "https://online.moysklad.ru/api/remap/1.2/download/{}",
        "BUNDLES": "https://online.moysklad.ru/api/remap/1.2/entity/bundle",
        "BUNDLE_DETAIL": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}",
        "BUNDLE_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}/images",
        "COMPONENTS": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}/components",
    }
    
    @staticmethod
    def moysklad_request(url_name: str="PRODUCTS", url_params: list=[]) -> dict:
        response = requests.get(
            MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
            headers=MoySklad.HEADERS
        )
        return response.json()

    @staticmethod
    def moysklad_patch(url_name: str, url_params: list=[], body_params: dict={}) -> dict:
        response = requests.get(
            MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
            headers=MoySklad.HEADERS,
            json=body_params
        )
        return response.json()
