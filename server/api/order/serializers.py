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
            "address", "code", "apartment_number", "floor_number", "intercom",
        )
        depth = 1


class OrderProductsSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = models.Order2ModificationModel
        fields = (
            "product", "quantity",
        )

    def get_product(self, obj):
        return products_serializers.ShortModificationSerializer(
            obj.product_modification_model
        ).data


class ViewOrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderModel
        fields = (
            "id", "name", "surname", "email", "phone",
            "receiving", "payment_type", "amount",
            "address", "code", "apartment_number", "floor_number", "intercom",
            "is_paid", "is_received", "products",
            "order_date", "status", "receiving_date",
            "loyalty_received", "loaylty_awarded"
        )
        depth = 1

    def get_products(self, obj):
        return OrderProductsSerializer(
            models.Order2ModificationModel.objects.filter(
                order_model=obj
            ),
            many=True,
        ).data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = "__all__"
        
        
class ProductsCalculateSerializer(serializers.Serializer):
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.IntegerField()
    size = serializers.CharField()
    color = serializers.CharField()
    message = serializers.CharField(allow_blank=True)
    status = serializers.CharField()
    image = serializers.CharField()

    class Meta:
        fields = (
            "name", "quantity", "price", "size", "image", "color", "message", "status"
        )

class CalculateSerializer(serializers.Serializer):
    products = ProductsCalculateSerializer(many=True)
    available_loyalty = serializers.IntegerField()
    price = serializers.IntegerField()

    class Meta:
        fields = [
            "products", "available_loyalty", "price"
        ]
