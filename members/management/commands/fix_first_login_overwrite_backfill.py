import logging
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from members.models import Member


class Command(BaseCommand):
    help = """
    Usage: python manage.py fix_first_login_overwrite_backfill
    
    Backfill (corrects) the first login value of members whose value has been overwritten by the import

    The `import_members` action was overwriting the value to be None if first login date is not available in the sheet,
    without considering if a value exists already. For future, this has been fixed, but we need to correct the value for
    existing members using their entry logs.

    This command sets the `Member.first_login_at` value to be the first EntryLog's date+time.
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        count = 0
        error_count = 0

        logging.info(f'Members with first login value: {Member.objects.exclude(first_login_at__isnull=True).count()}')

        for member in Member.objects.all():
            first_entry = member.member_logs.order_by('entered_date').first()

            if first_entry:
                timestamp = datetime.combine(first_entry.entered_date, first_entry.entered_time)

                if not member.first_login_at or member.first_login_at.date() > first_entry.entered_date:
                    try:
                        logging.info(f'Updating first login for member {member.member_id} from {member.first_login_at} to {timestamp}')

                        member.first_login_at = timestamp
                        member.save(update_fields=['first_login_at'])
                        count += 1
                    except Exception as e:
                        logging.error(f'Error updating member: {e}')
                        error_count += 1

        logging.info(f'Updated {count} members. {error_count} errors.')
