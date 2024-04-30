from rest_framework import serializers
from api.profile import models


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AddressModel
        fields = [
            "id", "user_id", "type", "address", "apartment_number", "floor_number", "intercom"
        ]
