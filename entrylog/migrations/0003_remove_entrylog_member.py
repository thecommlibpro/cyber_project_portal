# Generated by Django 4.2.2 on 2024-11-24 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entrylog', '0002_entrylog_member_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entrylog',
            name='member',
        ),
    ]
