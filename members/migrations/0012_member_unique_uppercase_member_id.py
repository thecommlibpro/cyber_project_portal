# Generated by Django 4.2.2 on 2024-11-26 15:30

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0011_alter_member_member_id'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='member',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper('member_id'), name='unique_uppercase_member_id', violation_error_message='Member ID already exists'),
        ),
    ]