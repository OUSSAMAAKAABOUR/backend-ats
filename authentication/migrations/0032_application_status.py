# Generated by Django 5.0.3 on 2024-07-05 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0031_alter_recruiter_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('p', 'Pending'), ('a', 'Accepted'), ('r', 'Rejected')], default='p', max_length=20),
        ),
    ]
