from django.db import models


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
    
    class Meta:
        db_table = "profile__loyalty"
        verbose_name = "Лояльность"
        verbose_name_plural = "Лояльность"
    
    def __str__(self) -> str:
        return f"{self.user.name} {self.user.surname}: {self.status} {self.balance}"
    
    
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
