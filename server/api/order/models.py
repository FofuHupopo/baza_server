from django.db import models

from api.authentication import models as auth_models
from api.products import models as product_models


class OrderModel(models.Model):
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
            ("receiving", "Доставка"),
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
    
    products_modification = models.ManyToManyField(
        product_models.ProductModificationModel,
        through="Order2ModificationModel",
        verbose_name="Модификации продуктов"
    )
    
    class Meta:
        db_table = "order__order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
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

    class Meta:
        db_table = "order__order2modification"
        verbose_name = "Заказ к модификации товара"
        verbose_name_plural = "Заказ к модификациям товаров"
        unique_together = ('order_model', 'product_modification_model')

    def save(self, *args, **kwargs) -> None:
        try: 
            basket_instance = Order2ModificationModel.objects.get(
                order_model=self.order_model,
                product_modification_model=self.product_modification_model
            )
            
            basket_instance.quantity += 1
            
            basket_instance.save()
        except Order2ModificationModel.DoesNotExist:
            return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.product_modification_model.product.name} ({self.product_modification_model.color.name}, {self.product_modification_model.size.name}) - {self.quantity}"
