# Generated by Django 4.2.2 on 2023-07-28 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='moember_name',
            new_name='member_name',
        ),
    ]
