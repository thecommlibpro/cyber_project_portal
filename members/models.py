import uuid

from django.db import models
from django.db.models.functions import Upper


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
    is_sticker_received = models.BooleanField(default=None, null=True, blank=True)
    first_login_at = models.DateTimeField(null=True, blank=True)
    cyber_project_enabled = models.BooleanField(default=False)

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
        return super().save(*args, **kwargs)
