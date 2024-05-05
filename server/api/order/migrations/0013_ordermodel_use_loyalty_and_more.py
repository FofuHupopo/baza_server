# Generated by Django 4.2.11 on 2024-05-05 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_remove_order2modificationmodel_baza_loyalty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='use_loyalty',
            field=models.BooleanField(default=False, verbose_name='Использовать баллы?'),
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='use_loyalty_balance',
            field=models.IntegerField(default=0, verbose_name='Использованная сумма баллов'),
        ),
        migrations.AlterField(
            model_name='ordermodel',
            name='receiving',
            field=models.CharField(choices=[('personal', 'Доставка'), ('cdek', 'Пункт СДЕК'), ('pickup', 'Самовывоз')], max_length=32, verbose_name='Способ получения'),
        ),
    ]