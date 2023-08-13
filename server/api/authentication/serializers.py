import re
from rest_framework import serializers


class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    
    def validate_phone(self, value):
        phone = PhoneNumberSerializer.clear_phone(value)
        
        if len(phone) != 11:
            raise serializers.ValidationError("Номер телефона не соответствует формату.")
        
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
            raise serializers.ValidationError("Номер телефона не соответствует формату.")

        return phone
    
    @staticmethod
    def clear_phone(phone: str) -> str:
        phone = phone.replace("+7", "8")
        phone = re.sub(r"\D", "", phone)

        return phone
