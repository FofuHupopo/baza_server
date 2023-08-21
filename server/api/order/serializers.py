from rest_framework import serializers

from . import models
from api.products import serializers as products_serializers


class OrderSerializer(serializers.ModelSerializer):
    products_modification = products_serializers.ListProductModificationSerializer(many=True)

    class Meta:
        model = models.OrderModel
        fields = (
            "id", "name", "surname", "email", "phone",
            "receiving", "payment_type",
            "city", "street", "house", "frame", "apartment",
            "is_paid", "products_modification"
        )
        depth = 1
