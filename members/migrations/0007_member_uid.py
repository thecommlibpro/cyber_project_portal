# Generated by Django 4.2.2 on 2024-11-21 22:43
from email.policy import default

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_remove_member_id_alter_member_member_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='uid',
            field=models.UUIDField(default=None, editable=False, unique=False, null=True),
        ),
    ]
