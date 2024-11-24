from django.db import migrations
import uuid


def populate_uuid_field(apps, schema_editor):
    Member = apps.get_model('members', 'Member')
    for member in Member.objects.all():
        member.uid = uuid.uuid4()
        member.save(update_fields=['uid'])


class Migration(migrations.Migration):
    dependencies = [
        ('members', '0007_member_uid'),
    ]

    operations = [
        migrations.RunPython(populate_uuid_field, reverse_code=migrations.RunPython.noop),
    ]
