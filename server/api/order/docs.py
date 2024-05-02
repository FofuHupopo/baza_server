from rest_framework import serializers


class PreCalculateSerialzier(serializers.Serializer):
    quantity = serializers.IntegerField()
    slug = serializers.SlugField(default="dress-maxi-00676-belyi-os")


class PostPreCalculateSerialzier(serializers.Serializer):
    products = PreCalculateSerialzier(many=True)
