# Generated by Django 4.2.11 on 2024-08-04 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0021_alter_dolyamemodel_payment_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dolyamemodel',
            name='amount',
            field=models.FloatField(blank=True, null=True, verbose_name='Сумма в копейках'),
        ),
        migrations.AlterField(
            model_name='dolyamemodel',
            name='residual_amount',
            field=models.FloatField(blank=True, null=True, verbose_name='Сумма подлежащая погашению'),
        ),
    ]