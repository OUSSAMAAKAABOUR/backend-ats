# Generated by Django 5.0.6 on 2024-07-15 11:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0035_clients_message_userstatus"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="in_call",
            field=models.BooleanField(default=False),
        ),
    ]
