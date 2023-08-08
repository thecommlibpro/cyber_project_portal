# Generated by Django 4.2.2 on 2023-08-08 10:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('members', '0006_remove_member_id_alter_member_member_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('library', models.CharField(choices=[('The Community Library Project - Khirki', 'The Community Library Project - Khirki'), ('The Community Library Project - Sikanderpur', 'The Community Library Project - Sikanderpur'), ('The Community Library Project - South Ex', 'The Community Library Project - South Ex')], default='The Community Library Project - Khirki', max_length=50)),
                ('datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('laptop_common_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_common_1', to='members.member')),
                ('laptop_common_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_common_2', to='members.member')),
                ('laptop_disability', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_disability', to='members.member')),
                ('laptop_education', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_education', to='members.member')),
                ('laptop_non_male_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_non_male_1', to='members.member')),
                ('laptop_non_male_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptop_non_male_2', to='members.member')),
            ],
            options={
                'unique_together': {('library', 'datetime')},
            },
        ),
    ]
