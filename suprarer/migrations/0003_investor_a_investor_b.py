# Generated by Django 4.1.7 on 2023-04-03 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("suprarer", "0002_investor_processed"),
    ]

    operations = [
        migrations.AddField(
            model_name="investor",
            name="a",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="investor",
            name="b",
            field=models.IntegerField(default=1),
        ),
    ]
