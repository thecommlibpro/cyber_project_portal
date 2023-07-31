# Generated by Django 4.2.2 on 2023-07-28 14:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0003_remove_slot_datetime_slot_date_slot_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slot',
            name='date',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='time',
        ),
        migrations.AddField(
            model_name='slot',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
