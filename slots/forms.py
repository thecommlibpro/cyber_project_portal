from typing import Any, Dict, Mapping, Optional, Type, Union
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django_select2 import forms as s2forms
from django import forms
from . import models
from slots.models import Slot, Member
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

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
    
    '''
    Rules for member slot management system -
    1. members have to be at least 11 years old.
    2. No member of any gender can take 2 slots in the same day.

    Rules for Sunday to Friday:
    3. All members can take slots only on alternative days, except Saturday
    4. Education slots can be taken daily.
    5. 2 laptops are reserved for girls, transgender, and non-binary members (no male member can take this slot, even when it is empty)

    On Saturdays:
    6. 5 laptops (education, for all, reserved for girls) are only for girls, transgender, and non-binary members (no male member can take this slot, even when it is empty)  
    7. Alternative days rules not applicable for Girls, trans and NB people on Saturdays. 
    '''
    def clean(self):
        cleaned_data = super().clean()
        changed_data = self.changed_data
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        library = cleaned_data["library"]
        date = str(cleaned_data["datetime"].date())
        weekday = parse(date).isoweekday()
        ''' 6 is Saturday '''

        ## 1
        for laptop_name in changed_data:
            if cleaned_data[laptop_name]:
                member_id = cleaned_data[laptop_name].member_id
                member_age = Member.objects.filter(member_id=member_id)[0].age
                if member_age < 11:
                    raise forms.ValidationError(f'Member {member_id} has to be of age 11 years or older')
            
        # 2
        member_list = []
        for laptop_name in laptop_list:
            member_list += self.get_member_list(library, date, laptop_name)
        for changed_field in changed_data:
            if cleaned_data[changed_field]:
                member_id = cleaned_data[changed_field].member_id
                if member_id in member_list:
                    raise forms.ValidationError(f"Member {member_id} has already taken a slot today")
        
        #3
        prev_date = str(parse(date).date() - relativedelta(days=1))
        for changed_field in changed_data:
            if cleaned_data[changed_field]:
                member_gender = cleaned_data[changed_field].gender
                #4, #7
                if changed_field != 'laptop_education' or (weekday !=6 and member_gender != Member.Gender.male):
                    member_id = cleaned_data[changed_field].member_id
                    if self.check_if_member_enrolled_prev_day(member_id, library, prev_date):
                        raise forms.ValidationError(f"Member {member_id} took a slot yesterday")
        
        #5, #6
        for changed_field in changed_data:
            if cleaned_data[changed_field]:
                member_gender = cleaned_data[changed_field].gender
                member_id = cleaned_data[changed_field].member_id
                if member_gender == Member.Gender.male:
                    if weekday ==6:
                        non_male_laptop_list = laptop_list[:]
                        non_male_laptop_list.remove("laptop_disability")
                    else:
                        non_male_laptop_list = ["laptop_non_male_1", "laptop_non_male_2"]
                    if changed_field in non_male_laptop_list:
                        raise forms.ValidationError(f"Member {member_id} is male and not allowed to take laptop {changed_field}")

        return cleaned_data

    def get_member_list(self, library, date, laptop):
        kwargs = {
            "library": library,
            "datetime__startswith": date,
            laptop+"__isnull": False
        }
        filtered_query_set = Slot.objects.filter(**kwargs)
        member_id_list = [getattr(z, laptop).member_id for z in filtered_query_set]
        return member_id_list
    
    # Except Education slot
    def check_if_member_enrolled_prev_day(self, member_id, library, date):
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        for laptop in laptop_list:
            #4
            if laptop != "laptop_education":
                kwargs = {
                    "library": library,
                    "datetime__startswith": date,
                    laptop: member_id
                }
                filtered_query_set = Slot.objects.filter(**kwargs)
                if len(filtered_query_set) != 0:
                    return True
            return False
