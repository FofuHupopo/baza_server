# Generated by Django 4.2.4 on 2023-08-23 09:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0014_colorimagemodel_productcolorimagesmodel_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcolormodel",
            name="eng_name",
            field=models.CharField(
                blank=True,
                max_length=127,
                null=True,
                verbose_name="Английское название",
            ),
        ),
        migrations.AddField(
            model_name="productmodificationmodel",
            name="slug",
            field=models.SlugField(
                blank=True, max_length=255, null=True, unique=True, verbose_name="Слаг"
            ),
        ),
    ]
