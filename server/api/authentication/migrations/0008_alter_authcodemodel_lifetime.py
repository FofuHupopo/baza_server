# Generated by Django 4.2.2 on 2023-06-28 20:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_alter_authcodemodel_lifetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authcodemodel',
            name='lifetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 28, 20, 46, 1, 986975, tzinfo=datetime.timezone.utc), verbose_name='Lifetime'),
        ),
    ]
