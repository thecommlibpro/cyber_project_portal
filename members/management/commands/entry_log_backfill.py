import logging

from django.core.management.base import BaseCommand

from entrylog.models import EntryLog
from members.models import Member
from slots.models import LibraryNames


class Command(BaseCommand):
    help = """
    Usage: python manage.py entry_log_backfill
    
    Create EntryLog records for members who had first_login_at before we started using the entrylog module. Excludes
    'MN-XXX' members as Sec 43 library is closed now.
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        members = Member.objects.filter(first_login_at__isnull=False).exclude(member_id__icontains='MN-')

        for member in members:
            first_entry = member.member_logs.order_by('entered_date', 'entered_time').first()
            library_code = member.member_id.split('-')[0]

            if not first_entry or first_entry.entered_date != member.first_login_at.date():
                logging.info(f"Creating entry log for {member.member_id} at {member.first_login_at}")

                entry_log = EntryLog.objects.create(
                    member=member,
                    library=LibraryNames.get_library(library_code),
                )

                EntryLog.objects.filter(pk=entry_log.id).update(
                    entered_date=member.first_login_at.date(),
                    entered_time=member.first_login_at.time(),
                )

        return
