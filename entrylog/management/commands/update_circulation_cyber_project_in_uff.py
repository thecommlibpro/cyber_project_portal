import csv
import logging
from datetime import datetime
from dateutil.parser import parse as date_parse
from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from entrylog.models import EntryLog
from members.models import Member
from slots.models import Slot, LibraryNames
from django.db.models import Q
from django.db import transaction

logging.basicConfig(level=logging.INFO, filename='update_circulation_cyber_project_in_uff.log')

class Command(BaseCommand):
    help = """
    Usage: python manage.py update_circulation_cyber_project_in_uff --circulation-file path/to/circulation.csv

    This command:
    1. Reads circulation.csv and creates EntryLog records for members whose last checkout
       is more recent than their last EntryLog
    2. Checks Slot records and creates EntryLog records if a member's first slot is
       after their first EntryLog
    """
    CUT_OFF_DATE = datetime(2024, 1, 1).date()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {
            'circulation_processed': 0,
            'circulation_created_missing': 0,    # when no EntryLog exists
            'circulation_created_newer': 0,      # when checkout date is more recent
            'circulation_skipped': 0,
            'circulation_errors': 0,             # when exceptions occur
            'slots_processed': 0,
            'slots_created_missing': 0,          # when no EntryLog exists
            'slots_created_earlier': 0,          # when slot date is earlier
            'slots_skipped': 0,
            'slots_errors': 0,                   # when exceptions occur
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--circulation-file',
            type=str,
            help='Path to the circulation.csv file',
            required=True
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without committing to database'
        )

    def handle(self, *args, **options):
        circulation_file = options['circulation_file']
        dry_run = options.get('dry_run', False)

        try:
            with transaction.atomic():
                self.process_circulation_data(circulation_file)
                self.process_slot_data()
                self.print_summary()

                if dry_run:
                    logging.info('Completed dry run - all changes will be rolled back')
                    transaction.set_rollback(True)
                else:
                    logging.info('Successfully processed circulation and slot data')
        except Exception as e:
            logging.error(f"Error commiting to database: {e}")

    def print_summary(self):
        logging.info("\nSummary:")
        logging.info(f"Circulation records processed: {self.stats['circulation_processed']}")
        logging.info(f"Circulation records created (no previous entry): {self.stats['circulation_created_missing']}")
        logging.info(f"Circulation records created (newer checkout): {self.stats['circulation_created_newer']}")
        logging.info(f"Circulation records skipped: {self.stats['circulation_skipped']}")
        logging.info(f"Circulation errors: {self.stats['circulation_errors']}")
        logging.info(f"\nSlot records processed: {self.stats['slots_processed']}")
        logging.info(f"Slot records created (no previous entry): {self.stats['slots_created_missing']}")
        logging.info(f"Slot records created (earlier slot): {self.stats['slots_created_earlier']}")
        logging.info(f"Slot records skipped: {self.stats['slots_skipped']}")
        logging.info(f"Slot errors: {self.stats['slots_errors']}\n")

    def process_circulation_data(self, circulation_file):
        with open(circulation_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                self.stats['circulation_processed'] += 1
                member_id = row.get('MemberID')
                try:
                    member_id = member_id.strip()
                    checkout_date = row.get('Last checkout')

                    if not member_id or not checkout_date:
                        self.stats['circulation_skipped'] += 1
                        logging.warning(f"Skipping row - missing member_id or checkout_date: {row}")
                        continue

                    member = Member.objects.filter(member_id=member_id.upper()).first()
                    checkout_date = date_parse(checkout_date).date()

                    if not member:
                        self.stats['circulation_skipped'] += 1
                        logging.warning(f"Member {member_id} not found")
                        continue

                    if checkout_date < self.CUT_OFF_DATE:
                        self.stats['circulation_skipped'] += 1
                        logging.warning(f"Skipping row - checkout_date is before 2024-01-01: {member_id} {checkout_date}")
                        continue

                    # Get last EntryLog for this member
                    first_entry = EntryLog.objects.filter(member=member).order_by('entered_date').first()

                    # If no EntryLog exists or checkout is more recent, create new EntryLog
                    if not first_entry or checkout_date > first_entry.entered_date:
                        # Get member's library from their ID (e.g., KH-123 -> Khirki)
                        library_code = member_id.split('-')[0]
                        try:
                            library = LibraryNames.get_library(library_code)
                        except Exception as e:
                            self.stats['circulation_skipped'] += 1
                            logging.warning(f"Skipping entry - error getting library for code '{library_code}': {e}")
                            continue

                        EntryLog.objects.create(
                            member=member,
                            library=library,
                            entered_date=checkout_date
                        )

                        # Update counter based on condition
                        if not first_entry:
                            self.stats['circulation_created_missing'] += 1
                            log_msg = "no previous entry"
                        else:
                            self.stats['circulation_created_newer'] += 1
                            log_msg = f"newer than previous {first_entry.entered_date}"

                        logging.info(f"Created EntryLog for member {member_id} on {checkout_date} ({log_msg})")

                        member.first_login_at = datetime.combine(checkout_date, datetime.min.time())
                        member.save()

                except Exception as e:
                    self.stats['circulation_errors'] += 1
                    logging.error(f"Error processing row for member {member_id}: {e}")

    def process_slot_data(self):
        try:
            # Get all members who have slot records
            members_with_slots = Member.objects.filter(
                Q(laptop_common_1__isnull=False) |
                Q(laptop_common_2__isnull=False) |
                Q(laptop_non_male_1__isnull=False) |
                Q(laptop_non_male_2__isnull=False) |
                Q(laptop_education__isnull=False) |
                Q(laptop_disability__isnull=False) |
                Q(laptop_adult_common_1__isnull=False) |
                Q(laptop_adult_non_male__isnull=False)
            ).distinct()

            logging.info(f"Found {len(members_with_slots)} members with slots")

            for member in members_with_slots:
                self.stats['slots_processed'] += 1

                logging.info(f"Processing slots for member {member.member_id}")

                try:
                    # Get member's first slot date across all laptop types
                    first_slot = Slot.objects.exclude(datetime__lt=self.CUT_OFF_DATE).filter(
                        Q(laptop_common_1=member) |
                        Q(laptop_common_2=member) |
                        Q(laptop_non_male_1=member) |
                        Q(laptop_non_male_2=member) |
                        Q(laptop_education=member) |
                        Q(laptop_disability=member) |
                        Q(laptop_adult_common_1=member) |
                        Q(laptop_adult_non_male=member)
                    ).order_by('datetime').first()

                    if not first_slot:
                        continue

                    # Get member's first EntryLog
                    first_entry = EntryLog.objects.filter(member=member).order_by('entered_date').first()

                    # If no EntryLog exists or first slot is before first entry, create new EntryLog
                    if not first_entry or first_slot.datetime.date() < first_entry.entered_date:
                        # Get member's library from their ID
                        library_code = member.member_id.split('-')[0]
                        try:
                            library = LibraryNames.get_library(library_code)
                        except Exception as e:
                            self.stats['slots_skipped'] += 1
                            logging.warning(f"Skipping entry - error getting library for code '{library_code}': {e}")
                            continue

                        EntryLog.objects.create(
                            member=member,
                            library=library,
                            entered_date=first_slot.datetime.date()
                        )

                        # Update counter based on condition
                        if not first_entry:
                            self.stats['slots_created_missing'] += 1
                            log_msg = "no previous entry"
                        else:
                            self.stats['slots_created_earlier'] += 1
                            log_msg = f"earlier than previous {first_entry.entered_date}"

                        logging.info(f"Created EntryLog for member {member.member_id} on {first_slot.datetime.date()} ({log_msg})")

                        member.first_login_at = first_slot.datetime
                        member.save()

                except Exception as e:
                    self.stats['slots_errors'] += 1
                    logging.error(f"Error processing slots for member {member.member_id}: {e}")

        except Exception as e:
            self.stats['slots_errors'] += 1
            logging.error(f"Error processing slot data: {e}")
