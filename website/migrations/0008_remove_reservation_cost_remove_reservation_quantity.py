# Generated by Django 5.0.6 on 2024-05-20 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_reservation_cost_reservation_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='quantity',
        ),
    ]
