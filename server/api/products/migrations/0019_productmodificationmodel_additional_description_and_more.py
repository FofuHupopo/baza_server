# Generated by Django 4.2.4 on 2023-08-26 18:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0018_productmodificationmodel_visible"),
    ]

    operations = [
        migrations.AddField(
            model_name="productmodificationmodel",
            name="additional_description",
            field=models.TextField(default="", verbose_name="Дополнительное описание"),
        ),
        migrations.AlterField(
            model_name="productmodel",
            name="visible",
            field=models.BooleanField(
                default=False, verbose_name="Отображается на сайте?"
            ),
        ),
    ]