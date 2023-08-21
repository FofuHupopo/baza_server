from rest_framework import serializers

from . import models


class ListOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderModel
   