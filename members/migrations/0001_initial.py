# Generated by Django 4.2.2 on 2023-06-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_id', models.TextField()),
                ('moember_name', models.TextField()),
            ],
        ),
    ]
