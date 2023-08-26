# Generated by Django 4.2.4 on 2023-08-26 18:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0020_alter_productmodificationmodel_additional_description"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productmodificationmodel",
            name="additional_description",
        ),
        migrations.AddField(
            model_name="productcolorimagesmodel",
            name="additional_description",
            field=models.TextField(
                blank=True,
                default="",
                null=True,
                verbose_name="Дополнительное описание к цвету",
            ),
        ),
    ]