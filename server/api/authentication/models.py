from __future__ import annotations
import re
import random
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager

from api.products.models import ProductModificationModel, ProductModel


class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Почта", unique=True,
        null=True, blank=True,
    )
    phone = models.CharField(
        "Номер телефона", max_length=14,
        unique=True, null=False,
    )
    name = models.CharField(
        "Имя", max_length=64,
        blank=True, null=True,
    )
    surname = models.CharField(
        "Фамилия", max_length=64,
        blank=True, null=True,
    )
    birthday_date = models.DateField(
        "День рождения",
        null=True, blank=True,
    )
    
    favorites = models.ManyToManyField(
        ProductModel, blank=True,
        verbose_name="Избранное"
    )
    basket = models.ManyToManyField(
        ProductModificationModel, blank=True,
        verbose_name="Корзина"
    )

    is_active = models.BooleanField(
        "Активный", default=True, help_text="Пользователь может авторизироваться"
    )
    is_superuser = models.BooleanField(
        "Администратор",
        default=False
    )
    @property
    def is_staff(self):
        return self.is_superuser

    date_joined = models.DateTimeField(
        "Дата регистрации", default=timezone.now
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "authentication__user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs) -> UserModel:
        self.phone = self.clear_phone(self.phone)

        return super(UserModel, self).save(*args, **kwargs)
    
    @staticmethod
    def clear_phone(phone: str) -> str:
        phone = phone.replace("+7", "8")
        phone = re.sub(r"\D", "", phone)

        return phone

    def format_phone(self):
        if "8" != self.phone[0]:
            raise ValueError("uncorrect phone number")
        
        phone = self.phone[1:]
        
        return f"+7 ({phone[0:3]}) {phone[3:6]} {phone[6:8]}-{phone[8:10]}"


class AuthCodeModel(models.Model):
    phone = models.CharField(
        "Phone", max_length=14
    )
    code = models.CharField(
        "Code", max_length=6
    )
    lifetime = models.DateTimeField(
        "Lifetime",
        default=timezone.now() + timedelta(minutes=5)
    )
    
    class Meta:
        db_table = "authentication__authcode"
        verbose_name = "Код авторизации"
        verbose_name_plural = "Коды авторизации"

    def __str__(self) -> str:
        return f"AuthCodeModel(phone={self.phone}, code={self.code})"

    @staticmethod
    def generate_code(phone: str) -> AuthCodeModel:
        return AuthCodeModel.objects.create(
            phone=phone,
            code=random.randint(111111, 999999)
        )
        
    @staticmethod
    def check_code(phone: str, code: str) -> bool:
        authcode = AuthCodeModel.objects.filter(
            phone=phone,
            code=code
        ).first()
        
        if authcode and authcode.lifetime > timezone.now():
            authcode.delete()
            return True

        return False
