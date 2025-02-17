# Generated by Django 5.0.3 on 2024-06-07 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_post_image_post_localisation_post_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='number_of_people_to_hire',
            field=models.CharField(default=-202, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='salary',
            field=models.FloatField(default=-2024, max_length=100),
            preserve_default=False,
        ),
    ]
