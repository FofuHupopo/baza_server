from rest_framework import serializers


class PostCalculateSerialzier(serializers.Serializer):
    delivery_type = serializers.CharField(default="pickup")
