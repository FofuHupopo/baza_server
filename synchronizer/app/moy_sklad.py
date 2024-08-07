import os
import requests
import time
from dotenv import load_dotenv


load_dotenv()


class MoySklad:
    MOYSKLAD_TOKEN = os.getenv("MOYSKLAD_TOKEN")
    HEADERS = {
        "Authorization": f"Bearer {MOYSKLAD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    }
    BASE_API_URL = "https://api.moysklad.ru/api/remap/1.2/"
    MOYSKLAD_URLS = {
        "PRODUCTS": BASE_API_URL + "entity/product?filter=archived=false",
        "PRODUCT_DETAIL": BASE_API_URL + "entity/product/{}",
        "MODIFICATIONS": BASE_API_URL + "entity/variant?filter=productid={}",
        "MODIFICATION_IMAGES": BASE_API_URL + "entity/variant/{}/images",
        "PRODUCT_IMAGES": BASE_API_URL + "entity/product/{}/images",
        "ASSORTMENT": BASE_API_URL + "entity/assortment?filter=id={}",
        "DOWNLOAD": BASE_API_URL + "download/{}",
        "BUNDLES": BASE_API_URL + "entity/bundle",
        "BUNDLE_DETAIL": BASE_API_URL + "entity/bundle/{}",
        "BUNDLE_IMAGES": BASE_API_URL + "entity/bundle/{}/images",
        "COMPONENTS": BASE_API_URL + "entity/bundle/{}/components",
        "WEBHOOK": BASE_API_URL + "entity/webhook",
        "WEBHOOK_ID": BASE_API_URL + "entity/webhook/{}",
    }
    
    @staticmethod
    def moysklad_request(url_name: str="PRODUCTS", url_params: list=[]) -> dict:
        def _response():
            response = requests.get(
                MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
                headers=MoySklad.HEADERS
            )
            return response.json()

        for _ in range(2):
            try:
                return _response()
            except requests.exceptions.ConnectTimeout:
                print("ConnectionTimeout, retry by 5 seconds...")
                time.sleep(5)
                
    @staticmethod
    def moysklad_post(url_name: str="PRODUCTS", url_params: list=[], query_params: dict={}, data_params: dict={}) -> dict:
        def _response():
            response = requests.post(
                MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
                headers=MoySklad.HEADERS,
                params=query_params,
                json=data_params
            )
            return response.json()

        for _ in range(2):
            try:
                return _response()
            except requests.exceptions.ConnectTimeout:
                print("ConnectionTimeout, retry by 5 seconds...")
                time.sleep(5)
                
    @staticmethod
    def moysklad_delete(url_name: str="PRODUCTS", url_params: list=[]) -> dict:
        def _response():
            response = requests.delete(
                MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
                headers=MoySklad.HEADERS
            )
            return

        for _ in range(2):
            try:
                return _response()
            except requests.exceptions.ConnectTimeout:
                print("ConnectionTimeout, retry by 5 seconds...")
                time.sleep(5)

    @staticmethod
    def moysklad_patch(url_name: str, url_params: list=[], body_params: dict={}) -> dict:
        response = requests.get(
            MoySklad.MOYSKLAD_URLS[url_name].format(*url_params),
            headers=MoySklad.HEADERS,
            json=body_params
        )
        return response.json()
