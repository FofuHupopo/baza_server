# Generated by Django 4.2.4 on 2023-08-26 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0019_productmodificationmodel_additional_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productmodificationmodel",
            name="additional_description",
            field=models.TextField(
                blank=True,
                default="",
                null=True,
                verbose_name="Дополнительное описание",
            ),
        ),
    ]
