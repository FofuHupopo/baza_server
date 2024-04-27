from rest_framework import serializers
from api.profile import models


class LoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LoyaltyModel
        fields = [
            "user_id", "status", "balance", "awaiting_balance", "remained"
        ]


class LoyaltyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LoyaltyHistoryModel
        fields = [
            "user_id", "datetime", "operation", "value", "total"
        ]
