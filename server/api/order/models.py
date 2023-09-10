from __future__ import annotations
from typing import List

from django.db import models
from django.utils import timezone

from api.authentication import models as auth_models
from api.products import models as product_models

from .consts import TAXES, TAXATIONS
from .settings import get_config


class OrderModel(models.Model):
    class OrderStatusChoice(models.TextChoices):
        CREATED = "created"
        PAID = "paid"
        IN_DELIVERY = "in_delivery"
        DELIVERED = "delivered"
        RECEIVED = "received"


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
            ("delivery_address", "Доставка до двери"),
            ("delivery_stock", "Доставка до склада"),
            ("pickup", "Самовывоз")
        ],
        max_length=32
    )
    
    payment_type = models.CharField(
        "Способ оплаты",
        choices=[
            ("online", "Картой онлайн"),
            ("cash", "Наличными"),
            ("fps", "СБП")
        ],
        max_length=32
    )
    
    city = models.CharField(
        "Город", max_length=128,
        null=True, blank=True
    )
    street = models.CharField(
        "Улица", max_length=128,
        null=True, blank=True
    )
    house = models.CharField(
        "Дом", max_length=16,
        null=True, blank=True
    )
    
    frame = models.CharField(
        "Корпус", max_length=16,
        null=True, blank=True
    )
    apartment = models.CharField(
        "Квартира", max_length=16,
        null=True, blank=True
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
    
    baza_loyalty = models.IntegerField(
        "Бонусная программа", default=0
    )
    loaylty_awarded = models.BooleanField(
        "Баллы начислены?", default=False
    )
    
    class Meta:
        db_table = "order__order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def save(self, *args, **kwargs) -> OrderModel:
        if self.status == self.OrderStatusChoice.PAID and not self.loaylty_awarded:
            for product in self.products.all():
                self.baza_loyalty += product.baza_loyalty
        
        if self.status == self.OrderStatusChoice.IN_DELIVERY and not self.receiving_date:
            self.receiving_date = timezone.now()
            # self.receiving_date = get_delivery_date()
            
        if self.status == self.OrderStatusChoice.DELIVERED and not self.is_received:
            self.is_received = True 
            
        if self.receiving == "pickup":
            self.city = None
            self.street = None
            self.house = None
            self.frame = None
            self.apartment = None

        return super(OrderModel, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.pk}: {self.name} {self.surname}"
    
    
    
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
    baza_loyalty = models.IntegerField(
        "Бонусная программа", default=0
    )

    class Meta:
        db_table = "order__order2modification"
        verbose_name = "Заказ к модификации товара"
        verbose_name_plural = "Заказ к модификациям товаров"
        unique_together = ('order_model', 'product_modification_model')
    
    def __str__(self) -> str:
        return f"{self.product_modification_model.product.name} ({self.product_modification_model.color.name}, {self.product_modification_model.size.name}) - {self.quantity}"


# class Payment(models.Model):
#     RESPONSE_FIELDS = {
#         'Success': 'success',
#         'Status': 'status',
#         'PaymentId': 'payment_id',
#         'ErrorCode': 'error_code',
#         'PaymentURL': 'payment_url',
#         'Message': 'message',
#         'Details': 'details',
#     }

#     amount = models.IntegerField(verbose_name='Сумма в копейках', editable=False)
#     order_id = models.CharField(verbose_name='Номер заказа', max_length=100, unique=True, editable=False)
#     description = models.TextField(verbose_name='Описание', max_length=250, blank=True, default='', editable=False)

#     success = models.BooleanField(verbose_name='Успешно проведен', default=False, editable=False)
#     status = models.CharField(verbose_name='Статус транзакции', max_length=20, default='', editable=False)
#     payment_id = models.CharField(
#         verbose_name='Уникальный идентификатор транзакции в системе банка', max_length=20, default='', editable=False)
#     error_code = models.CharField(verbose_name='Код ошибки', max_length=20, default='', editable=False)
#     payment_url = models.CharField(
#         verbose_name='Ссылка на страницу оплаты.',
#         help_text='Ссылка на страницу оплаты. По умолчанию ссылка доступна в течении 24 часов.',
#         max_length=100, blank=True, default='', editable=False)
#     message = models.TextField(verbose_name='Краткое описание ошибки', blank=True, default='', editable=False)
#     details = models.TextField(verbose_name='Подробное описание ошибки', blank=True, default='', editable=False)

#     class Meta:
#         verbose_name = 'Транзакция'
#         verbose_name_plural = 'Транзакции'

#     def __str__(self):
#         return f'Транзакция #{self.pk}:{self.order_id}:{self.payment_id}'

#     def can_redirect(self) -> bool:
#         return self.status == 'NEW' and self.payment_url

#     def is_paid(self) -> bool:
#         return self.status == 'CONFIRMED' or self.status == 'AUTHORIZED'

#     def with_receipt(self, email: str, taxation: str = None, phone: str = '') -> 'Payment':
#         if not self.id:
#             self.save()

#         if hasattr(self, 'receipt'):
#             return self

#         Receipt.objects.create(payment=self, email=email, phone=phone)

#         return self

#     def with_items(self, items: List[dict]) -> 'Payment':
#         for item in items:
#             ReceiptItem.objects.create(**item, receipt=self.receipt)
#         return self

#     def to_json(self) -> dict:
#         data = {
#             'Amount': self.amount,
#             'OrderId': self.order_id,
#             'Description': self.description,
#         }

#         if hasattr(self, 'receipt'):
#             data['Receipt'] = self.receipt.to_json()

#         return data


# class Receipt(models.Model):
#     payment = models.OneToOneField(to=Payment, on_delete=models.CASCADE, verbose_name='Платеж')
#     email = models.CharField(
#         verbose_name='Электронный адрес для отправки чека покупателю', max_length=64)
#     phone = models.CharField(verbose_name='Телефон покупателя', max_length=64, blank=True, default='')
#     taxation = models.CharField(verbose_name='Система налогообложения', choices=TAXATIONS, max_length=20)

#     class Meta:
#         verbose_name = 'Данные чека'
#         verbose_name_plural = 'Данные чеков'

#     def __str__(self):
#         return '{self.id} ({self.payment})'.format(self=self)

#     def save(self, *args, **kwargs):
#         if not self.taxation:
#             self.taxation = get_config()['TAXATION']

#         return super().save(*args, **kwargs)

#     def to_json(self) -> dict:
#         return {
#             'Email': self.email,
#             'Phone': self.phone,
#             'Taxation': self.taxation,
#             'Items': [item.to_json() for item in self.receiptitem_set.all()]
#         }


# class ReceiptItem(models.Model):
#     receipt = models.ForeignKey(to=Receipt, on_delete=models.CASCADE, verbose_name='Чек')
#     name = models.CharField(verbose_name='Наименование товара', max_length=128)
#     price = models.IntegerField(verbose_name='Цена в копейках')
#     quantity = models.DecimalField(verbose_name='Количество/вес', max_digits=20, decimal_places=3)
#     amount = models.IntegerField(verbose_name='Сумма в копейках')
#     tax = models.CharField(verbose_name='Ставка налога', max_length=10, choices=TAXES)
#     ean13 = models.CharField(verbose_name='Штрих-код', max_length=20, blank=True, default='')
#     shop_code = models.CharField(verbose_name='Код магазина', max_length=64, blank=True, default='')

#     class Meta:
#         verbose_name = 'Информация о товаре'
#         verbose_name_plural = 'Информация о товарах'

#     def __str__(self):
#         return '{self.id} (Чек {self.receipt.id})'.format(self=self)

#     def save(self, *args, **kwargs):
#         if not self.amount:
#             self.amount = self.price * self.quantity
#         if not self.tax:
#             self.tax = get_config()['ITEM_TAX']
#         return super().save(*args, **kwargs)

#     def to_json(self) -> dict:
#         return {
#             'Name': self.name,
#             'Price': self.price,
#             'Quantity': self.quantity,
#             'Amount': self.amount,
#             'Tax': self.tax,
#             'Ean13': self.ean13,
#             'ShopCode': self.shop_code,
#         }