# Generated by Django 4.2.dev20230116175929 on 2023-01-16 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userlocation",
            name="accuracy_meters",
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
