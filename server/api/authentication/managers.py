import re
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, **extra_fields):
        user = self.model(**extra_fields)
        
        phone = user.clear_phone(phone)
        user.phone = phone
        
        user.set_password(phone)
        user.save()

        return user

    def create_superuser(self, phone, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(phone, **extra_fields)
