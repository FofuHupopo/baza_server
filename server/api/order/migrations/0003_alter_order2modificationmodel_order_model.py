# Generated by Django 4.2.4 on 2023-08-23 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0002_rename_number_ordermodel_house"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order2modificationmodel",
            name="order_model",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="order.ordermodel",
                verbose_name="Заказ",
            ),
        ),
    ]
