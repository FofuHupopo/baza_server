# Generated by Django 4.2.4 on 2023-08-23 14:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0015_productcolormodel_eng_name_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productcategorymodel",
            old_name="category",
            new_name="name",
        ),
    ]
