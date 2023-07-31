from django_select2 import forms as s2forms
from django import forms
from . import models

class MemberWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "member_id__icontains",
        "member_name__icontains",
    ]

class SlotForm(forms.ModelForm):
    class Meta:
        model = models.Slot
        fields = "__all__"
        widgets = {
            "member": MemberWidget
        }