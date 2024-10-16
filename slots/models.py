from django.db import models

from django.db import models
from members.models import Member
from datetime import datetime

class SlotTimes(models.TextChoices):
     am8 = ("8:00 am", "8:00 am")
     am830 = ("8:30 am", "8:30 am")
     am9 = ("9:00 am", "9:00 am")
     am930 = ("9:30 am", "9:30 am")
     am10 = ("10:00 am", "10:00 am")
     am1030 = ("10:30 am", "10:30 am")
     am11 = ("11:00 am", "11:00 am")
     am1130 = ("11:30 am", "11:30 am")
     pm12 = ("12:00 pm", "12:00 pm")
     pm1230 = ("12:30 pm", "12:30 pm")
     pm1 = ("1:00 pm", "1:00 pm")
     pm130 = ("1:30 pm", "1:30 pm")
     pm2 = ("2:00 pm", "2:00 pm")
     pm230 = ("2:30 pm", "2:30 pm")
     pm3 = ("3:00 pm", "3:00 pm")
     pm330 = ("3:30 pm", "3:30 pm")
     pm4 = ("4:00 pm", "4:00 pm")
     pm430 = ("4:30 pm", "4:30 pm")
     pm5 = ("5:00 pm", "5:00 pm")
     pm530 = ("5:30 pm", "5:30 pm")
     pm6 = ("6:00 pm", "6:00 pm")
     pm630 = ("6:30 pm", "6:30 pm")
     pm7 = ("7:00 pm", "7:00 pm")
     pm730 = ("7:30 pm", "7:30 pm")



class LibraryNames(models.TextChoices):
    TCLP_01 = ("The Community Library Project - Khirki", "The Community Library Project - Khirki")
    TCLP_02 = ("The Community Library Project - Sikanderpur", "The Community Library Project - Sikanderpur")
    # TCLP_03 = ("The Community Library Project - Sec 43", "The Community Library Project - Sec 43")
    TCLP_04 = ("The Community Library Project - South Ex", "The Community Library Project - South Ex")

class LaptopCategories(models.TextChoices):
    laptop_common_1 = ("Common Laptop - 1", "Common Laptop - 1")
    laptop_common_2 = ("Common Laptop - 2", "Common Laptop - 2")
    laptop_non_male_1 = ("Laptop for girls and Trans members - 1", "Laptop for girls and Trans members - 1")
    laptop_non_male_2 = ("Laptop for girls and Trans members - 2", "Laptop for girls and Trans members - 2")
    laptop_education = ("Laptop for education", "Laptop for education")
    laptop_disability = ("Laptop for disabled", "Laptop for disabled")
    laptop_adult_common_1 = ("Laptop for adults - Common", "Laptop for adults - Common")
    laptop_adult_non_male = ("Laptop for adults - T, NB, and Women", "Laptop for adults - T, NB, and Women")


class Slot(models.Model):

    class Meta:
        unique_together = (('library', 'datetime'))
        ordering = ['datetime']

    library = models.CharField(max_length=50, choices=LibraryNames.choices, default=LibraryNames.TCLP_01)
    datetime = models.DateTimeField(default=datetime.now)
    # member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    laptop_common_1 = models.ForeignKey(Member, verbose_name="Laptop for All - 1", related_name='laptop_common_1', on_delete=models.CASCADE, null=True, blank=True)
    laptop_common_2 = models.ForeignKey(Member, verbose_name="Laptop for All - 2", related_name='laptop_common_2', on_delete=models.CASCADE, null=True, blank=True)
    laptop_non_male_1 = models.ForeignKey(Member, verbose_name="Laptop for Girls, T, NB - 1", related_name='laptop_non_male_1', on_delete=models.CASCADE, null=True, blank=True)
    laptop_non_male_2 = models.ForeignKey(Member, verbose_name="Laptop for Girls, T, NB - 2", related_name='laptop_non_male_2', on_delete=models.CASCADE, null=True, blank=True)
    laptop_education = models.ForeignKey(Member, verbose_name="Laptop for Education", related_name='laptop_education', on_delete=models.CASCADE, null=True, blank=True)
    laptop_disability = models.ForeignKey(Member, verbose_name="Laptop for P w Disabilities", related_name='laptop_disability', on_delete=models.CASCADE, null=True, blank=True)
    laptop_adult_common_1 = models.ForeignKey(Member, verbose_name="Laptop for adults - Common", related_name='laptop_adult_common_1', on_delete=models.CASCADE, null=True, blank=True)
    laptop_adult_non_male = models.ForeignKey(Member, verbose_name="Laptop for adults - T, NB, and Women", related_name='laptop_adult_non_male', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.datetime)
