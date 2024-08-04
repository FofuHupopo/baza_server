import decimal
import json
from uuid import UUID

from api.request import BotServer
from .models import OrderModel, models, Order2ModificationModel


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


def send_bot_order(order: OrderModel, products: list[Order2ModificationModel]):
    BotServer.new_order({
            "order_id": str(order.id),
            "receiving": order.receiving,
            "address": order.address,
            "code": order.code,
            "is_express": order.is_express,
            "floor_number": order.floor_number,
            "apartment_number": order.apartment_number,
            "intercom": order.intercom,
            "comment": order.comment,
            "user_id": order.user.pk,
            "user_name": order.user.name,
            "user_surname": order.user.surname,
            "user_phone": order.user.phone,
            "user_email": order.user.email,
            "products": [
                {
                    "name": product.product_modification_model.product.name,
                    "color": product.product_modification_model.color.name,
                    "size": product.product_modification_model.size.name,
                    "quantity": product.quantity,
                    "code": product.product_modification_model.product.code,
                    "url": f"https://thebaza.ru/products/{product.product_modification_model.slug[:-1]}"
                }
                for product in products
            ]
        })
