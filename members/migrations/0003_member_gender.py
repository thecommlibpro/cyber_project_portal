# Generated by Django 4.2.2 on 2023-07-29 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_rename_moember_name_member_member_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Female', max_length=10),
        ),
    ]
