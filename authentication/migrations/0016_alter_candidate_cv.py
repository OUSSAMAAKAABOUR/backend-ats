
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0015_recruiter_address_recruiter_city_recruiter_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
