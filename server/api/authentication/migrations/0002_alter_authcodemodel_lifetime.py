# Generated by Django 4.2.2 on 2023-06-28 16:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authcodemodel',
            name='lifetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 28, 16, 59, 14, 39689, tzinfo=datetime.timezone.utc), verbose_name='Lifetime'),
        ),
    ]
