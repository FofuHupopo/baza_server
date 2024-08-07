# Generated by Django 4.2.11 on 2024-05-05 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0028_productmodificationmodel_reserve_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productmodificationmodel',
            old_name='reserve_quantity',
            new_name='quantity_reserve',
        ),
        migrations.RemoveField(
            model_name='productmodificationmodel',
            name='quantity',
        ),
        migrations.AddField(
            model_name='productmodificationmodel',
            name='quantity_store',
            field=models.IntegerField(default=0, verbose_name='Количество на складе'),
        ),
    ]
