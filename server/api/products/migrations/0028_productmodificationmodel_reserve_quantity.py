# Generated by Django 4.2.11 on 2024-05-05 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_productmodel_composition_and_care'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodificationmodel',
            name='reserve_quantity',
            field=models.IntegerField(default=0, verbose_name='Заразервированный товар'),
        ),
    ]