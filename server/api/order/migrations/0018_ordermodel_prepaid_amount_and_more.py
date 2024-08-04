# Generated by Django 4.2.11 on 2024-08-03 17:07

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_receiptitem_name_alter_receiptitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='prepaid_amount',
            field=models.IntegerField(blank=True, null=True, verbose_name='Сумма аванса'),
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='payment_type',
            field=models.CharField(choices=[('online', 'Картой онлайн'), ('cash', 'Наличными'), ('dolyame', 'Долями'), ('sbp', 'СБП')], max_length=32, verbose_name='Способ оплаты'),
        ),
        migrations.CreateModel(
            name='DolyameModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(default='', editable=False, max_length=20, verbose_name='Статус транзакции')),
                ('amount', models.IntegerField(editable=False, verbose_name='Сумма в копейках')),
                ('residual_amount', models.IntegerField(editable=False, verbose_name='Сумма подлежащая погашению')),
                ('payment_url', models.CharField(blank=True, default='', editable=False, max_length=100, verbose_name='Ссылка на страницу оплаты.')),
                ('payment_fail', models.BooleanField(default=False, verbose_name='Оплата провалена')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.ordermodel', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Доляме',
                'verbose_name_plural': 'Доляме',
                'db_table': 'dolyame',
            },
        ),
    ]
