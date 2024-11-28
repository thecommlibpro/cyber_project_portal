# Generated by Django 4.2.2 on 2024-11-26 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_member_unique_uppercase_member_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='cyber_project_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='member',
            name='first_login_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='is_sticker_received',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]