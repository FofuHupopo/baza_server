import json
from aiohttp.web_response import json_response
from aiohttp.web_request import Request

from db.repository import OrderRepository
from bot.utils import notify_managers


async def new_order_handler(request: Request):
    body = await request.json()
    
    order_id = body["order_id"]
    data = {
        "receiving": body["receiving"],
        "is_express": body.get("is_express", False),
        "address": body.get("address", None),
        "code": body.get("code", None),
        "apartment_number": body.get("apartment_number", None),
        "floor_number": body.get("floor_number", None),
        "intercom": body.get("intercom", None),
        "products": json.dumps(body.get("products", [])),
    }
    
    order = OrderRepository.create_order(
        order_id=order_id,
        **data
    )
    
    receiving_ru = {
        "personal": "Доставка",
        "cdek": "Пункт СДЕК",
        "pickup": "Самовывоз",
    }.get(order.receiving, "")
    
    message = "Основная информация:\n" \
        f"\tID: {order_id}\n" \
        f"\t\tID заказчика: {order.user_id}\n" \
        f"\tСпособ получения: {receiving_ru}\n"

    if order.receiving == "cdek":
        message += f"\tАдрес ПВЗ: {order.address}\n" \
            f"\tКод ПВЗ: {order.code}\n"

    if order.receiving == "personal":
        message += f"\tАдрес: {order.address}\n" \
            f"\tЭкспресс доставка: {'да' if order.is_express else 'нет'}\n" \
            f"\tНомер этажа: {order.floor_number}\n" \
            f"\tНомер квартиры: {order.apartment_number}\n" \
            f"\tДомофон: {order.intercom}\n"

    message += f"\tИнформация о получателе:\n" \
        f"\t\tИмя: {order.user_name}\n" \
        f"\t\tФамилия: {order.user_surname}\n" \
        f"\t\tТелефон: {order.user_phone}\n" \
        f"\t\tПочта: {order.user_email}\n" \

    message += f"\tТовары:\n"
    for product in json.loads(order.products):
        message += f"\t\t{'=' * 40}\n" \
            f"\t\tСсылка: {product.get('url', '')}\n" \
            f"\t\tАртикул: {product.get('code', '')}\n" \
            f"\t\tНазвание: {product.get('name', '')}\n" \
            f"\t\tЦвет: {product.get('color', '')}\n" \
            f"\t\tРазмер: {product.get('size', '')}\n" \
            f"\t\tКоличество: {product.get('quantity', 0)}\n" \
            f"\t\t{'=' * 40}\n" \

    await notify_managers(f"Появился новый заказ.\n{message}")
    
    return json_response({"status": "ok"})
