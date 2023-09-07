from django_select2 import forms as s2forms
from django import forms
from . import models
from slots.models import Member

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
            "member": MemberWidget,
            "laptop_common_1": MemberWidget,
            "laptop_common_2": MemberWidget,
            "laptop_non_male_1": MemberWidget,
            "laptop_non_male_2": MemberWidget,
            "laptop_education": MemberWidget,
            "laptop_disability": MemberWidget,
        }
    
    def clean_age(self):
        print("PPPPPPPP")
        member_id = self.cleaned_data["laptop_common_1"]
        member_age = Member.objects.filter(member_id=member_id)[0].age
        if member_age < 11:
            raise forms.ValidationError('Member has to be of age 11 years or older')