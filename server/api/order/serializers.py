from rest_framework import serializers

from . import models
from api.products import serializers as products_serializers
from api.products import models as product_models


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderModel
        fields = (
            "id", "name", "surname", "email", "phone",
            "receiving", "payment_type",
            "city", "street", "house", "frame", "apartment"
        )
        depth = 1


class OrderProductsSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = models.Order2ModificationModel
        fields = (
            "product", "quantity", "baza_loyalty"
        )

    def get_product(self, obj):
        return products_serializers.ShortModificationSerializer(
            obj.product_modification_model,
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
            "receiving", "payment_type", "amount",
            "city", "street", "house", "frame", "apartment",
            "is_paid", "is_received", "products",
            "order_date", "status", "receiving_date", "baza_loyalty"
        )
        depth = 1

    def get_products(self, obj):
        return OrderProductsSerializer(
            models.Order2ModificationModel.objects.filter(
                order_model=obj
            ),
            many=True,
            context={
                "request": self.context["request"]
            }
        ).data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = "__all__"


class PreCalculateSerializer(serializers.Serializer):
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.IntegerField()
    size = serializers.CharField()
    color = serializers.CharField()
    message = serializers.CharField(allow_blank=True)
    status = serializers.CharField()

    class Meta:
        fields = (
            "name", "quantity", "price", "size", "color", "message", "status"
        )
