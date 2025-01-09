from datetime import datetime
from functools import cached_property
from dateutil.parser import parse as date_parse
from django.db import models

from members.models import Member
from slots.models import LibraryNames


class EntryLog(models.Model):
    DEFAULT_START_DATE = date_parse('2022-01-01')
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='member_logs',
    )
    library = models.CharField(choices=LibraryNames.choices, max_length=50, null=False, blank=False)
    entered_date = models.DateField(auto_now_add=True)
    entered_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.member_id} ({self.member_name}) - {self.entered_date} {self.entered_time.strftime('%H:%M')} - {self.library_location}"

    @cached_property
    def library_location(self):
        return self.library.split('-')[1].strip()

    @cached_property
    def member_name(self):
        return self.member.member_name

    @classmethod
    def filtered(cls, library=None, start=None, end=None):
        start = start or cls.DEFAULT_START_DATE
        end = end or datetime.today()
        entry_logs = cls.objects.filter(
            entered_date__range=(start, end),
        )

        if library:
            entry_logs = entry_logs.filter(library=library)

        return entry_logs

    @cached_property
    def timestamp(self):
        return datetime.combine(self.entered_date, self.entered_time)
