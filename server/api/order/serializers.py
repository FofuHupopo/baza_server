from rest_framework import serializers

from . import models
from api.products import serializers as products_serializers


class CreateOrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderModel
        fields = (
            "id", "name", "surname", "email", "phone",
            "receiving", "payment_type",
            "city", "street", "house", "frame", "apartment",
            "is_paid", "products"
        )
        depth = 1

    def get_products(self, obj):
        return products_serializers.CartSerializer(
            models.Order2ModificationModel.objects.filter(
                order_model=obj
            ),
            many=True,
            context={
                "request": self.context["request"]
            }
        ).data


class ViewOrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderModel
        fields = (
            "id", "name", "surname", "email", "phone",
            "receiving", "payment_type",
            "city", "street", "house", "frame", "apartment",
            "is_paid", "is_received", "products",
            "order_date", "status", "receiving_date", "baza_loyalty"
        )
        depth = 1

    def get_products(self, obj):
        return products_serializers.CartSerializer(
            models.Order2ModificationModel.objects.filter(
                order_model=obj
            ),
            many=True,
            context={
                "request": self.context["request"]
            }
        ).data