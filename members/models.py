import uuid

from django.db import models

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
    member_name = models.TextField(null=True)

    class Gender(models.TextChoices):
        male = "Male"
        female = "Female"
        gender_non_conforming = "Gender non-conforming"
        non_binary = "Non-binary"
        prefer_not_to_say = "Prefer not to say"
        transgender = "Transgender"

    gender = models.CharField(max_length=30, choices=Gender.choices, default=Gender.female, null=True)

    age = models.IntegerField(null=True)
    # is_sticker_received = models.BooleanField(default=None, null=True, blank=True)
    # first_login_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return str(self.member_id) + " - " + str(self.member_name) + " - " + str(self.age) + " - " + str(self.gender)

    def save(self, *args, **kwargs):
        self.member_id = self.member_id.upper()
        return super().save(*args, **kwargs)
