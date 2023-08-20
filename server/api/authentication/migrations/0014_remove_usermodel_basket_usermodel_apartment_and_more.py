# Generated by Django 4.2.4 on 2023-08-19 11:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0013_productmodel_old_price"),
        ("authentication", "0013_alter_authcodemodel_lifetime"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usermodel",
            name="basket",
        ),
        migrations.AddField(
            model_name="usermodel",
            name="apartment",
            field=models.CharField(
                blank=True, max_length=16, null=True, verbose_name="Квартира"
            ),
        ),
        migrations.AddField(
            model_name="usermodel",
            name="city",
            field=models.CharField(
                blank=True, max_length=128, null=True, verbose_name="Город"
            ),
        ),
        migrations.AddField(
            model_name="usermodel",
            name="frame",
            field=models.CharField(
                blank=True, max_length=16, null=True, verbose_name="Корпус"
            ),
        ),
        migrations.AddField(
            model_name="usermodel",
            name="number",
            field=models.CharField(
                blank=True, max_length=16, null=True, verbose_name="Дом"
            ),
        ),
        migrations.AddField(
            model_name="usermodel",
            name="street",
            field=models.CharField(
                blank=True, max_length=128, null=True, verbose_name="Улица"
            ),
        ),
        migrations.CreateModel(
            name="BasketModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=0, verbose_name="Количество"),
                ),
                (
                    "product_modification_model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.productmodificationmodel",
                        verbose_name="Модификация продукта",
                    ),
                ),
                (
                    "user_model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзины",
                "db_table": "profile__basket",
                "unique_together": {("user_model", "product_modification_model")},
            },
        ),
    ]