# Generated by Django 4.2.2 on 2023-06-28 16:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcolormodel',
            name='hex_code',
            field=models.CharField(blank=True, max_length=6, null=True, validators=[django.core.validators.MinLengthValidator(6)], verbose_name='HEX цвета'),
        ),
    ]
