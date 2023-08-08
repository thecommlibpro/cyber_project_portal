from django.db import models

class Member(models.Model):
    member_id = models.CharField(max_length=30, null=False, primary_key=True)
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

    def __str__(self) -> str:
        return str(self.member_id) + " - " + str(self.member_name) + " - " + str(self.age) + " - " + str(self.gender)