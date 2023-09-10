# Generated by Django 4.2.4 on 2023-09-10 10:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0007_order2modificationmodel_baza_loyalty"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ordermodel",
            name="receiving",
            field=models.CharField(
                choices=[
                    ("delivery_address", "Доставка до двери"),
                    ("delivery_stock", "Доставка до склада"),
                    ("pickup", "Самовывоз"),
                ],
                max_length=32,
                verbose_name="Способ получения",
            ),
        ),
    ]
