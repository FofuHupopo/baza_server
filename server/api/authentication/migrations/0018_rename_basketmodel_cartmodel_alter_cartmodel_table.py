# Generated by Django 4.2.4 on 2023-08-28 17:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "products",
            "0021_remove_productmodificationmodel_additional_description_and_more",
        ),
        ("authentication", "0017_rename_number_usermodel_house"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="BasketModel",
            new_name="CartModel",
        ),
        migrations.AlterModelTable(
            name="cartmodel",
            table="profile__cart",
        ),
    ]
