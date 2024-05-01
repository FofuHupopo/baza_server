# -*- coding: utf-8 -*-

import uvicorn
import asyncio
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi.openapi.docs import get_swagger_ui_html

from utils import sort_by_similarity


# CONTSTANTS

URL = {
    "deliverypoints": "https://api.edu.cdek.ru/v2/deliverypoints",
    "cities": "https://api.cdek.ru/v2/location/cities/?country_codes=RU",
    "token": "https://api.edu.cdek.ru/v2/oauth/token"
}
CITIES = []
DELIVERY_POINTS = dict()
AUTH = {
    "client_id": "EMscd6r9JnFiQ3bLoyjJY6eM78JrJceI",
    "client_secret": "PjLZkKBHEiLK3YsjtNrt3TGNG0ahs3kG",
    "grant_type": "client_credentials",
    "token": ""
}

# PARSER
    
async def request(url: str, params: dict={}) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers={
            "Authorization": f'Bearer {AUTH["token"]}'
        }) as response:
            return await response.json()


async def cdek_auth():
     async with aiohttp.ClientSession() as session:
        async with session.post(URL["token"], params=AUTH) as response:
            if response.status == 200:
                AUTH["token"] = (await response.json()).get("access_token", "")
                print("CDEK_AUTH")
                return


async def get_cities():
    response = await request(URL["cities"])
    
    cities = []
    for city in response:
        cities.append(city["city"])

    CITIES.clear()
    CITIES.extend(cities)
    print("CITIES")


async def get_delivery_points():
    response = await request(URL["deliverypoints"], params={
        "weight_max": 10,
        "is_handout": 1,
    })

    delivery_points = dict()
    for delivery_point in response:
        city = delivery_point.get("location", {}).get("city", "")
        
        if not city or city not in CITIES:
            continue
        
        if delivery_points.get(city.lower()) is None:
            delivery_points[city.lower()] = []

        delivery_points[city.lower()].append({
            "code": delivery_point["code"],
            "city": city,
            "longitude": delivery_point["location"]["longitude"],
            "latitude": delivery_point["location"]["latitude"],
            "address": delivery_point["location"]["address"],
        })

    DELIVERY_POINTS.clear()
    DELIVERY_POINTS.update(delivery_points.items())
    
    print("DELIVERY_POINTS")
    

# MODELS

class DeliveryPointModel(BaseModel):
    code: str
    city: str
    longitude: float
    latitude: float
    address: str


# FASTAPI

app = FastAPI()

@app.get("/cities")
async def cities(request: Request) -> list[str]:
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    return JSONResponse(content=CITIES, headers=headers)


@app.get("/cities/search")
async def cities_search(request: Request, q: str) -> list[str]:
    query_words = q.lower()
    
    response = sort_by_similarity(query_words, CITIES)

    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    return JSONResponse(content=response[:5], headers=headers)


@app.get("/delivery-points")
async def cities_search(request: Request, city: str) -> list[DeliveryPointModel]:
    response = DELIVERY_POINTS.get(city.lower(), [])

    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    return JSONResponse(content=response[:5], headers=headers)


@app.get("/swagger", include_in_schema=False)
async def get_documentation(request: Request):
    return get_swagger_ui_html(openapi_url="/service/cdek/" + "/openapi.json", title="Swagger")


# SCHEDULED TASK

async def cdek_auth_task():
    while True:
        await cdek_auth()
        await asyncio.sleep(60 * 45)


async def get_cities_task():
    while True:
        await get_cities()
        await asyncio.sleep(60 * 60)


async def get_delivery_points_task():
    while True:
        await get_delivery_points()
        await asyncio.sleep(60 * 60)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cdek_auth_task())
    await asyncio.sleep(1)
    asyncio.create_task(get_cities_task())
    await asyncio.sleep(1)
    asyncio.create_task(get_delivery_points_task())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
