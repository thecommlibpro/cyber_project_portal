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
    TCLP_01 = "The Community Library Project - Khirki"
    TCLP_02 = "The Community Library Project - Sikanderpur"
    TCLP_03 = "The Community Library Project - Sec 43"
    TCLP_04 = "The Community Library Project - South Ex"


class Slot(models.Model):
    library = models.CharField(max_length=50, choices=LibraryNames.choices, default=LibraryNames.TCLP_01)
    datetime = models.DateTimeField(default=datetime.now)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return str(self.datetime)
