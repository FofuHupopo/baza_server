from __future__ import annotations
from typing import List

import uuid
from django.db import models
from django.utils import timezone

from api.authentication import models as auth_models
from api.products import models as product_models
from api.profile import models as profile_models

from .consts import TAXES, TAXATIONS
from .settings import get_config


class OrderModel(models.Model):
    class OrderStatusChoice(models.TextChoices):
        CREATED = "created"
        FAILED_PAYMENT = "failed_payment"
        PAID = "paid"
        AWAITING_DELIVERY = "awaiting_delivery"
        IN_DELIVERY = "in_delivery"
        DELIVERED = "delivered"
        RECEIVED = "received"
        CANCELLED = "cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        auth_models.UserModel, models.CASCADE,
        verbose_name="Пользователь"
    )

    name = models.CharField(
        "Имя клиента", max_length=128
    )
    surname = models.CharField(
        "Фамилия клиента", max_length=128
    )
    
    email = models.EmailField(
        "Почта клиента"
    )
    phone = models.CharField(
        "Телефон клиента", max_length=11
    )
    
    receiving = models.CharField(
        "Способ получения",
        choices=[
            ("personal", "Доставка"),
            ("cdek", "Пункт СДЕК"),
            ("pickup", "Самовывоз")
        ],
        max_length=32
    )
    
    payment_type = models.CharField(
        "Способ оплаты",
        choices=[
            ("online", "Картой онлайн"),
            ("cash", "Наличными"),
            ("sbp", "СБП")
        ],
        max_length=32
    )
    
    address = models.CharField(
        verbose_name="Адрес",
        null=True, blank=True
    )
    
    
    code = models.CharField(
        verbose_name="Код ПВЗ", default=None,
        null=True, blank=True
    )
    comment = models.TextField(
        verbose_name="Комментарий к заказу", default="",
        null=True, blank=True
    )
    apartment_number = models.IntegerField(
        verbose_name="Номер квартиры", default=None,
        null=True, blank=True
    )
    floor_number = models.IntegerField(
        verbose_name="Номер этажа", default=None,
        null=True, blank=True
    )
    intercom = models.IntegerField(
        verbose_name="Домофон", default=None,
        null=True, blank=True
    )
    is_express = models.BooleanField(
        "Экспресс доставка", default=False
    )

    is_paid = models.BooleanField(
        "Оплачено?", default=False
    )
    is_received = models.BooleanField(
        "Получен?", default=False
    )

    products = models.ManyToManyField(
        product_models.ProductModificationModel,
        through="Order2ModificationModel",
        verbose_name="Модификации продуктов"
    )

    order_date = models.DateTimeField(
        "Дата заказа", default=timezone.now
    )

    status = models.CharField(
        "Статус", max_length=32,
        choices=OrderStatusChoice.choices,
        default=OrderStatusChoice.CREATED
    )
    receiving_date = models.DateTimeField(
        "Дата получения",
        null=True, blank=True
    )

    use_loyalty = models.BooleanField(
        "Использовать баллы?", default=False
    )
    use_loyalty_balance = models.IntegerField(
        "Использованная сумма баллов", default=0
    )
    
    loyalty_received = models.IntegerField(
        "Полученные баллы", default=0
    )
    loaylty_awarded = models.BooleanField(
        "Баллы начислены?", default=False
    )

    amount = models.IntegerField(
        "Стоимость", default=0
    )

    class Meta:
        db_table = "order__order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def save(self, *args, **kwargs) -> OrderModel:
        if self.status == self.OrderStatusChoice.CREATED and not self.loyalty_received:
            loyalty, _ = profile_models.LoyaltyModel.objects.get_or_create(
                user=self.user
            )
            loyalty_percent = profile_models.LOYALTY_LEVELS.get(loyalty.status, {}).get("percent", 0)

            loyalty.awaiting_balance += loyalty_percent * self.amount
            loyalty.save()
    
            self.loyalty_received = loyalty_percent * self.amount

        if self.status == self.OrderStatusChoice.IN_DELIVERY and not self.receiving_date:
            self.receiving_date = timezone.now()
            
        if self.status == self.OrderStatusChoice.DELIVERED and not self.is_received:
            self.is_received = True

        if self.status == self.OrderStatusChoice.RECEIVED and not self.loaylty_awarded:
            loyalty, _ = profile_models.LoyaltyModel.objects.get_or_create(
                user=self.user
            )
            loyalty.balance += self.loyalty_received
            loyalty.awaiting_balance -= self.loyalty_received
            loyalty.save()
            
            profile_models.LoyaltyHistoryModel.create(self.user, self.loyalty_received, loyalty.balance)

            self.loaylty_awarded = True

        return super(OrderModel, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.pk}: {self.name} {self.surname}"
    
    def set_order_cancel(self):
        self.status = self.OrderStatusChoice.CANCELLED
        
        if self.is_paid:
            print("Возврат платежа...")

        self.save()


class Order2ModificationModel(models.Model):
    order_model = models.ForeignKey(
        OrderModel,
        verbose_name="Заказ",
        on_delete=models.CASCADE
    )
    product_modification_model = models.ForeignKey(
        product_models.ProductModificationModel,
        verbose_name="Модификация продукта",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        "Количество", default=0
    )

    class Meta:
        db_table = "order__order2modification"
        verbose_name = "Заказ к модификации товара"
        verbose_name_plural = "Заказ к модификациям товаров"
        unique_together = ('order_model', 'product_modification_model')
    
    def __str__(self) -> str:
        return f"{self.product_modification_model.product.name} ({self.product_modification_model.color.name}, {self.product_modification_model.size.name}) - {self.quantity}"


class Payment(models.Model):
    RESPONSE_FIELDS = {
        'Success': 'success',
        'Status': 'status',
        'PaymentId': 'payment_id',
        'ErrorCode': 'error_code',
        'PaymentURL': 'payment_url',
        'Message': 'message',
        'Details': 'details',
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    amount = models.IntegerField(verbose_name='Сумма в копейках', editable=False)
    order_id = models.CharField(verbose_name='Номер заказа', max_length=100, editable=False)
    description = models.TextField(verbose_name='Описание', max_length=250, blank=True, default='', editable=False)

    success = models.BooleanField(verbose_name='Успешно проведен', default=False, editable=False)
    status = models.CharField(verbose_name='Статус транзакции', max_length=20, default='', editable=False)
    payment_id = models.CharField(
        verbose_name='Уникальный идентификатор транзакции в системе банка', max_length=20, default='', editable=False)
    error_code = models.CharField(verbose_name='Код ошибки', max_length=20, default='', editable=False)
    payment_url = models.CharField(
        verbose_name='Ссылка на страницу оплаты.',
        help_text='Ссылка на страницу оплаты. По умолчанию ссылка доступна в течении 24 часов.',
        max_length=100, blank=True, default='', editable=False)
    message = models.TextField(verbose_name='Краткое описание ошибки', blank=True, default='', editable=False)
    details = models.TextField(verbose_name='Подробное описание ошибки', blank=True, default='', editable=False)
    
    payment_fail = models.BooleanField(
        "Ошибка платежа", default=False
    )

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'Транзакция #{self.pk}:{self.order_id}:{self.payment_id}'

    def can_redirect(self) -> bool:
        return self.status == 'NEW' and self.payment_url

    def is_paid(self) -> bool:
        return self.status == 'CONFIRMED' or self.status == 'AUTHORIZED'

    def with_receipt(self, email: str, phone: str = '') -> Payment:
        if not self.id:
            self.save()

        if hasattr(self, 'receipt'):
            return self

        Receipt.objects.create(payment=self, email=email, phone=phone)

        return self

    def with_items(self, items: List[dict]) -> Payment:
        for item in items:
            ReceiptItem.objects.create(**item, receipt=self.receipt)
        return self
    
    @staticmethod
    def create(**kwargs):
        try:
            payment = Payment.objects.get(
                order_id=kwargs.get("order_id"),
                payment_fail=False
            )

            return payment
        except Payment.DoesNotExist:
            return Payment.objects.create(**kwargs)

    @staticmethod
    def get(**kwargs):
        try:
            payment = Payment.objects.get(
                order_id=kwargs.get("order_id"),
                payment_fail=False
            )

            return payment
        except Payment.DoesNotExist:
            return Payment.objects.get(**kwargs)

    def set_payment_fail(self):
        self.payment_fail = True
        self.save()

    def to_json(self) -> dict:
        data = {
            'Amount': self.amount,
            'OrderId': self.order_id,
            'Description': self.description,
        }

        if hasattr(self, 'receipt'):
            data['Receipt'] = self.receipt.to_json()

        return data


class Receipt(models.Model):
    payment = models.OneToOneField(to=Payment, on_delete=models.CASCADE, verbose_name='Платеж')
    email = models.CharField(
        verbose_name='Электронный адрес для отправки чека покупателю', max_length=64)
    phone = models.CharField(verbose_name='Телефон покупателя', max_length=64, blank=True, default='')

    class Meta:
        verbose_name = 'Данные чека'
        verbose_name_plural = 'Данные чеков'

    def __str__(self):
        return f"{self.pk} ({self.payment})"

    def to_json(self) -> dict:
        return {
            'Email': self.email,
            'Phone': self.phone,
            'Taxation': 'usn_income',
            'Items': [item.to_json() for item in self.receiptitem_set.all()]
        }


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        verbose_name='Чек'
    )
    product = models.ForeignKey(
        product_models.ProductModificationModel, models.PROTECT,
        verbose_name="Товар",
        null=True, blank=True
    )
    name = models.CharField(
        verbose_name='Название', max_length=255,
        null=True, blank=True
    )
    price = models.IntegerField(verbose_name='Цена в копейках')
    quantity = models.IntegerField(verbose_name='Количество')
    amount = models.IntegerField(verbose_name='Сумма в копейках')

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Информация о товарах'

    def __str__(self):
        return f"{self.pk} (Чек {self.receipt.pk})"

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.price * self.quantity

        return super().save(*args, **kwargs)

    def to_json(self) -> dict:
        return {
            'Name': self.product.name if self.product else self.name,
            'Price': self.price,
            'Quantity': self.quantity,
            'Amount': self.amount,
            'Tax': 'none',
        }
