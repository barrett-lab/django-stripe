# Generated by Django 5.0.6 on 2024-06-07 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_file_file_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='file_name',
        ),
    ]
