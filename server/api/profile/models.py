from django.db import models
from django.utils import timezone


LOYALTY_LEVELS = {
    "black": {
        "min": 0,
        "percent": 0.05,
        "next": "gold"
    },
    "gold": {
        "min": 1000,
        "percent": 0.07,
        "next": "platinum",
        "pred": "black",
    },
    "platinum": {
        "min": 10000,
        "percent": 0.1,
        "next": None,
        "pred": "gold",
    },
}


class LoyaltyStatusModel(models.TextChoices):
    """Статус лояльности"""
    BLACK = "black"
    GOLD = "gold"
    PLATINUM = "platinum"


class LoyaltyModel(models.Model):
    user = models.OneToOneField(
        "authentication.UserModel",
        verbose_name="Пользователь",
        on_delete=models.CASCADE
    )
    
    status = models.CharField(
        verbose_name="Статус лояльности",
        choices=LoyaltyStatusModel.choices,
        default=LoyaltyStatusModel.BLACK
    )
    
    balance = models.IntegerField(
        verbose_name="Баланс лояльности",
        default=0
    )
    awaiting_balance = models.IntegerField(
        verbose_name="Ожидаемый баланс лояльности",
        default=0
    )

    remained = models.IntegerField(
        verbose_name="Остаталось до следущего уровня",
        default=0,
        blank=True, null=True
    )
    total_spent = models.IntegerField(
        verbose_name="Всего потрачено",
        default=0
    )
    
    class Meta:
        db_table = "profile__loyalty"
        verbose_name = "Лояльность"
        verbose_name_plural = "Лояльность"
    
    def __str__(self) -> str:
        return f"{self.user.name} {self.user.surname}: {self.status} {self.balance}"
    
    def confirm_balance(self, amount: int) -> None:
        awaiting_balance = min(self.awaiting_balance, amount)
        
        self.awaiting_balance -= awaiting_balance
        self.balance += awaiting_balance
        
        self.save()
        
    def add_awaiting_balance(self, amount: int) -> None:
        self.awaiting_balance += int(amount * LOYALTY_LEVELS.get(self.status).get("percent"))
        self.total_spent += amount
        
        self.save()
    
    @staticmethod
    def get_by_user_id(user_id):
        loyalty, _ = LoyaltyModel.objects.get_or_create(user_id=user_id)
        return loyalty
    
    def save(self, *args, **kwargs) -> None:
        if self.status not in LOYALTY_LEVELS:
            return super().save(*args, **kwargs)
    
        current_level = LOYALTY_LEVELS.get(self.status)        
        next_level = LOYALTY_LEVELS.get(current_level.get("next"))

        if not next_level:
            self.remained = 0
            return super().save(*args, **kwargs)

        self.remained = next_level.get("min") - self.total_spent
        
        if self.remained > 0:
            return super().save(*args, **kwargs)
        
        min_next_level = None
        min_next_balance = float("inf")
        
        for level, level_info in LOYALTY_LEVELS.items():
            if level_info.get("min") < self.total_spent:
                continue
            
            if level_info.get("min") < min_next_balance:
                min_next_balance = level_info.get("min")
                min_next_level = level
        
        if min_next_level is None:
            self.remained = None
            self.status = "platinum"
            return super().save(*args, **kwargs)
        
        self.status = LOYALTY_LEVELS.get(min_next_level).get("pred")
        self.remained = min_next_balance - self.total_spent
        
        return super().save(*args, **kwargs)
    
    
class LoyaltyOperationModel(models.TextChoices):
    """Операция лояльности"""
    MARKETING = "marketing"
    BRING_IN = "bring_in"


class LoyaltyHistoryModel(models.Model):
    user = models.ForeignKey(
        "authentication.UserModel",
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(
        verbose_name="Дата и время",
        default=timezone.now
    )
    operation = models.CharField(
        verbose_name="Баланс лояльности",
        choices=LoyaltyOperationModel.choices,
        default=LoyaltyOperationModel.MARKETING
    )
    value = models.IntegerField(
        verbose_name="История",
        default=0
    )
    total = models.IntegerField(
        verbose_name="Итого",
        default=0
    )
    
    class Meta:
        db_table = "profile__loyalty_history"
        verbose_name = "История лояльности"
        verbose_name_plural = "История лояльности"
    
    def __str__(self) -> str:
        return f"{self.user.name} {self.user.surname}: {self.operation}"


class AddressTypeChoices(models.TextChoices):
    """Тип адреса"""
    CDEK = "cdek"
    PERSONAL = "personal"


class AddressModel(models.Model):
    user = models.ForeignKey(
        "authentication.UserModel",
        on_delete=models.CASCADE
    )
    type = models.CharField(
        verbose_name="Тип адреса",
        max_length=128
    )
    address = models.CharField(
        verbose_name="Адрес",
        max_length=128
    )
    is_main = models.BooleanField(
        verbose_name="Основной адрес",
        default=False
    )

    code = models.CharField(
        verbose_name="Код ПВЗ", default=None,
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
    
    class Meta:
        db_table = "profile__address"
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
    
    def __str__(self) -> str:
        return f"{self.user.name} {self.user.surname}: {self.name} {self.address}"

    def user_addresses(self, user_id: int, type: str) -> models.QuerySet:
        if type in (AddressTypeChoices.CDEK, AddressTypeChoices.PERSONAL):
            return AddressModel.objects.filter(
                user_id=user_id,
                type=type
            )

        return AddressModel.objects.filter(
            user_id=user_id
        )
        
    def save(self, *args, **kwargs):
        if self.is_main:
            addresses = AddressModel.objects.filter(
                user=self.user
            )

            if hasattr(self, "pk") and self.pk:
                addresses = addresses.exclude(pk=self.pk)
            
            addresses.update(is_main=False)

        return super().save(*args, **kwargs)
