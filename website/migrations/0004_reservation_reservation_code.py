# Generated by Django 5.0.6 on 2024-05-20 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_remove_reservation_reservation_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='reservation_code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
