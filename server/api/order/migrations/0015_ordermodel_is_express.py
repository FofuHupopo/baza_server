# Generated by Django 4.2.11 on 2024-05-05 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_alter_ordermodel_address_alter_ordermodel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='is_express',
            field=models.BooleanField(default=False, verbose_name='Экспресс доставка'),
        ),
    ]
