# Generated by Django 4.2.4 on 2023-08-15 17:53

import api.authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0012_alter_authcodemodel_lifetime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authcodemodel",
            name="lifetime",
            field=models.DateTimeField(
                default=api.authentication.models.now_plus_5_minutes,
                verbose_name="Lifetime",
            ),
        ),
    ]
