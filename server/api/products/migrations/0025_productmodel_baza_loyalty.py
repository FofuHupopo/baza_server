# Generated by Django 4.2.11 on 2024-04-16 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_productmodificationmodel_booked'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='baza_loyalty',
            field=models.IntegerField(default=0, verbose_name='Баллы лояльности'),
        ),
    ]