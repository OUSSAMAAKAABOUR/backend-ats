# Generated by Django 5.0.4 on 2024-04-30 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internship',
            name='interns',
        ),
        migrations.AddField(
            model_name='internship',
            name='interns',
            field=models.ForeignKey(blank=True, default=1997, on_delete=django.db.models.deletion.CASCADE, related_name='internships', to='utils.intern'),
            preserve_default=False,
        ),
    ]
