# Generated by Django 5.0.3 on 2024-06-10 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0023_recruiter_comp_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiter',
            name='comp_description',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='recruiter',
            name='comp_industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
