# Generated by Django 5.0.4 on 2024-04-19 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_requirement_remove_post_requirements_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='requirements',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='post',
            new_name='company',
        ),
        migrations.DeleteModel(
            name='Requirement',
        ),
        migrations.AddField(
            model_name='post',
            name='requirements',
            field=models.JSONField(default='test'),
            preserve_default=False,
        ),
    ]
