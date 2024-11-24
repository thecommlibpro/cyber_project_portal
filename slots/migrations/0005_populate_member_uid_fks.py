
from django.db import migrations


def populate_uuid_fks(apps, schema_editor):
    Slot = apps.get_model('slots', 'Slot')
    for slot in Slot.objects.all():

        print(str(slot))

        slot.laptop_common_1_uid_id = slot.laptop_common_1 and slot.laptop_common_1.uid
        slot.laptop_common_2_uid_id = slot.laptop_common_2 and slot.laptop_common_2.uid
        slot.laptop_non_male_1_uid_id = slot.laptop_non_male_1 and slot.laptop_non_male_1.uid
        slot.laptop_non_male_2_uid_id = slot.laptop_non_male_2 and slot.laptop_non_male_2.uid
        slot.laptop_education_uid_id = slot.laptop_education and slot.laptop_education.uid
        slot.laptop_disability_uid_id = slot.laptop_disability and slot.laptop_disability.uid
        slot.laptop_adult_common_1_uid_id = slot.laptop_adult_common_1 and slot.laptop_adult_common_1.uid
        slot.laptop_adult_non_male_uid_id = slot.laptop_adult_non_male and slot.laptop_adult_non_male.uid

        slot.save()

class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0004_slot_laptop_adult_common_1_uid_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_uuid_fks, reverse_code=migrations.RunPython.noop),
    ]
