from rest_framework import serializers
from api.profile import models


class LoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LoyaltyModel
        fields = [
            "user_id", "balance", "awaiting_balance", "status", "remained"
        ]
