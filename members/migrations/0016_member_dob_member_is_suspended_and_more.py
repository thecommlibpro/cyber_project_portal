# Generated by Django 4.2.2 on 2025-05-12 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0015_alter_member_member_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='dob',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='is_suspended',
            field=models.BooleanField(default=False, help_text='Is suspended/retired?'),
        ),
        migrations.AddField(
            model_name='member',
            name='suspension_date',
            field=models.DateTimeField(blank=True, help_text='Suspension/Retire date', null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='suspension_end_at',
            field=models.DateTimeField(blank=True, help_text='Suspension end date', null=True),
        ),
    ]
