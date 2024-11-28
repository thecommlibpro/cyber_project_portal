# Generated by Django 4.2.2 on 2024-11-24 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_populate_uid'),
        ('slots', '0003_slot_laptop_adult_common_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='slot',
            name='laptop_adult_common_1_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_adult_common_1_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for adults - Common'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_adult_non_male_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_adult_non_male_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for adults - T, NB, and Women'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_common_1_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_common_1_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for All - 1'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_common_2_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_common_2_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for All - 2'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_disability_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_disability_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for P w Disabilities'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_education_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_education_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for Education'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_non_male_1_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_non_male_1_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for Girls, T, NB - 1'),
        ),
        migrations.AddField(
            model_name='slot',
            name='laptop_non_male_2_uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_non_male_2_uid_slots', to='members.member', to_field='uid', verbose_name='Laptop for Girls, T, NB - 2'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_adult_common_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_adult_common_1', to='members.member', verbose_name='Laptop for adults - Common'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_adult_non_male',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_adult_non_male', to='members.member', verbose_name='Laptop for adults - T, NB, and Women'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_common_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_common_1', to='members.member', verbose_name='Laptop for All - 1'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_common_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_common_2', to='members.member', verbose_name='Laptop for All - 2'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_disability',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_disability', to='members.member', verbose_name='Laptop for P w Disabilities'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_education',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_education', to='members.member', verbose_name='Laptop for Education'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_non_male_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_non_male_1', to='members.member', verbose_name='Laptop for Girls, T, NB - 1'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='laptop_non_male_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='laptop_non_male_2', to='members.member', verbose_name='Laptop for Girls, T, NB - 2'),
        ),
    ]