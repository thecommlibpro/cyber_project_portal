import logging
import uuid
from datetime import datetime
from typing import Optional

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models.functions import Upper
from requests.auth import HTTPBasicAuth

from utils import calculate_age


class Gender(models.TextChoices):
    male = "Male"
    female = "Female"
    gender_non_conforming = "Gender non-conforming"
    non_binary = "Non-binary"
    prefer_not_to_say = "Prefer not to say"
    transgender = "Transgender"

class Member(models.Model):
    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    member_id = models.CharField(
        unique=True,
        max_length=30,
        null=False,
    )
    member_name = models.CharField(max_length=1024, null=True, blank=True)
    gender = models.CharField(max_length=30, choices=Gender.choices, default=Gender.female, null=True)

    age = models.IntegerField(null=True)
    dob = models.DateField(null=True)
    is_sticker_received = models.BooleanField(default=None, null=True, blank=True)
    first_login_at = models.DateTimeField(null=True, blank=True)
    cyber_project_enabled = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False, help_text="Is suspended/retired?")
    suspension_date = models.DateTimeField(null=True, blank=True, help_text="Suspension/Retire date")
    suspension_end_at = models.DateTimeField(null=True, blank=True, help_text="Suspension end date")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Upper('member_id'),
                name='unique_uppercase_member_id',
                violation_error_message='Member ID already exists',
            ),
        ]

    def __str__(self) -> str:
        return str(self.member_id) + " - " + str(self.member_name) + " - " + str(self.age) + " - " + str(self.gender)

    def save(self, *args, **kwargs):
        self.member_id = self.member_id.strip().upper()
        self.member_name = self.member_name and self.member_name.strip()

        if self.dob:
            self.age = calculate_age(self.dob)

        return super().save(*args, **kwargs)

    @classmethod
    def fetch_from_koha(cls, member_id: str) -> Optional[dict]:
        auth = HTTPBasicAuth(settings.KOHA_API['USERNAME'], settings.KOHA_API['PASSWORD'])
        base_url = settings.KOHA_API['BASE_URL']

        response = requests.get(
            f'{base_url}/patrons/?cardnumber={member_id}',
            headers={
                'x-koha-embed': 'extended_attributes',
            },
            auth=auth,
        )

        logging.info(f'Fetched patron details ({member_id}) from Koha: {response.status_code} -> {response.url}')

        # We need an exact match, if there are multiple results then return None
        members = list(filter(lambda member: member['cardnumber'].upper() == member_id, response.json()))
        member_data = members[0] if len(members) == 1 else None

        if not member_data:
            return None

        member_data['name'] = (member_data['firstname'] or '') + f" {member_data['surname'] or ''}"

        for extended_attribute in member_data['extended_attributes']:
            member_data[extended_attribute['type']] = extended_attribute['value']

        return member_data

    @classmethod
    def get(cls, member_id, skip_koha=False) -> Optional["Member"]:
        member = cls.objects.filter(member_id=member_id).first()

        if skip_koha:
            return member

        member_data = cls.fetch_from_koha(member_id)

        if not member_data:
            return member

        if not member:
            member = cls()

        member.member_id = member_data['cardnumber']
        member.member_name = member_data['name']
        member.gender = Gender(member_data['Sex'])
        member.dob = member_data['date_of_birth']
        member.is_suspended = member_data.get('MS', None) in ['SUSPENDED', 'RETIRED']
        member.suspension_date = member_data.get('RE_SU_DATE')
        member.suspension_end_at = member_data.get('SU_END_DATE')

        member.save()
        member.refresh_from_db()

        return member

    def refresh_from_koha(self):
        return self.__class__.get(self.member_id)
