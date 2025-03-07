# Generated by Django 4.2.2 on 2024-11-24 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0009_alter_member_uid'),
        ('entrylog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entrylog',
            name='member_uid',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_logs', to='members.member', to_field='uid'),
        ),
    ]
