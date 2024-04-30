# Generated by Django 4.2.11 on 2024-04-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_alter_loyaltymodel_remained'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressmodel',
            name='apartment_number',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Номер квартиры'),
        ),
        migrations.AddField(
            model_name='addressmodel',
            name='floor_number',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Номер этажа'),
        ),
        migrations.AddField(
            model_name='addressmodel',
            name='intercom',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Домофон'),
        ),
    ]
