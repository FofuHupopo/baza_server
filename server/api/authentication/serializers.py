import re
from rest_framework import serializers

from . import models
from api.products import serializers as product_serializers
from api.products import models as products_models


class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    
    def validate_phone(self, value):
        phone = PhoneNumberSerializer.clear_phone(value)
        
        if len(phone) != 11:
            raise serializers.ValidationError("Номер телефона не соответствует формату.", 406)
        
        return phone
    
    @staticmethod
    def clear_phone(phone: str) -> str:
        phone = phone.replace("+7", "8")
        phone = re.sub(r"\D", "", phone)

        return phone


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate_phone(self, value):
        phone = PhoneNumberSerializer.clear_phone(value)
        
        if len(phone) != 11:
            raise serializers.ValidationError("Номер телефона не соответствует формату.", 406)

        return phone
    
    @staticmethod
    def clear_phone(phone: str) -> str:
        phone = phone.replace("+7", "8")
        phone = re.sub(r"\D", "", phone)

        return phone
    
    
class BasketSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = models.BasketModel
        fields = (
            "product", "quantity"
        )
        
    def get_product(self, obj):
        return product_serializers.ProductModificationSerializer(
            obj.product_modification_model,
            context=self.context
        ).data


class UserDataSerialzier(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True)
    favorites = product_serializers.ListProductSerializer(many=True)
    cart = serializers.SerializerMethodField()
    birthday_date = serializers.DateField(format="%d.%m.%Y", input_formats=['%d.%m.%Y', '%Y-%m-%d'])

    class Meta:
        model = models.UserModel
        fields = (
            "id", "email", "phone",
            "name", "surname", "birthday_date",
            "city", "street", "house", "frame", "apartment",
            "favorites", "cart"
        )

    def get_cart(self, obj):
        return product_serializers.ListProductsSerializer(
            models.BasketModel.objects.filter(
                user_model=obj
            ),
            many=True,
            context=self.context
        ).data


class UpdateUserInfoSerializer(serializers.ModelSerializer):
    birthday_date = serializers.DateField(format="%d.%m.%Y", input_formats=['%d.%m.%Y', '%Y-%m-%d'])

    class Meta:
        model = models.UserModel
        fields = (
            "email", "name", "surname", "birthday_date",
            "city", "street", "house", "frame", "apartment",
        )
