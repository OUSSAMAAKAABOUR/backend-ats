# Generated by Django 5.0.3 on 2024-06-25 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0027_event_recruiter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_end_date',
        ),
    ]
