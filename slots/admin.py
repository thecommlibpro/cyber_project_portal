from typing import Any
from django.http import HttpResponse
from django.contrib import admin
from .models import Slot
from django.contrib import messages
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from rangefilter.filters import DateRangeFilterBuilder, DateTimeRangeFilterBuilder, NumericRangeFilterBuilder
from django.template.defaultfilters import linebreaksbr
import easy
import csv

from .models import LibraryNames, SlotTimes, LaptopCategories
from .utils import generate_slots as generate_util
from .utils import *
from .forms import SlotForm
from django.db import connection

class GenerateSlotForm(ActionForm):
    library = forms.ChoiceField(choices=LibraryNames.choices, required=False)
    start_day = forms.DateField(widget=AdminDateWidget, required=False)
    end_day = forms.DateField(widget=AdminDateWidget, required=False)

class SlotAdmin(admin.ModelAdmin):

    def save_models(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        try:
            check_if_member_more_than_11_years(request)
            return super().save_model(request, obj, form, change)
        except forms.ValidationError:
            self.message_user(request=request, message='Member has to be of age 11 years or older', level=messages.ERROR)

    form = SlotForm
    action_form = GenerateSlotForm
    list_display = (
        'get_time',
        'wrapped_field_laptop_common_1',
        'wrapped_field_laptop_common_2',
        'wrapped_field_laptop_non_male_1',
        'wrapped_field_laptop_non_male_2',
        'wrapped_field_laptop_education',
        'wrapped_field_laptop_disability',
    )


    wrapped_field_laptop_common_1 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_common_1) if x.laptop_common_1 else "", 'Laptop for All - 1', 'Laptop for All - 1')
    wrapped_field_laptop_common_2 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_common_2) if x.laptop_common_2 else "", "Laptop for All - 2", "Laptop for All - 2")
    wrapped_field_laptop_non_male_1 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_non_male_1) if x.laptop_non_male_1 else "", "Laptop for Girls, T, NB - 1", "Laptop for Girls, T, NB - 1")
    wrapped_field_laptop_non_male_2 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_non_male_2) if x.laptop_non_male_2 else "", "Laptop for Girls, T, NB - 2", "Laptop for Girls, T, NB - 2")
    wrapped_field_laptop_education = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_education) if x.laptop_education else "", "Laptop for Education", "Laptop for Education")
    wrapped_field_laptop_disability = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_disability) if x.laptop_disability else "", "Laptop for P w Disabilities", "Laptop for P w Disabilities")

    @admin.display(description='Slot time')
    def get_time(self, obj):
        return obj.datetime.strftime("%Y-%m-%d %I:%M%p")

    @admin.display(ordering='member__member_name', description='Member name')
    def get_member_name(self, obj):
        return obj.member and obj.member.member_name
    
    @admin.display(ordering='member__gender', description='Member gender')
    def get_member_gender(self, obj):
        return obj.member and obj.member.gender
    
    search_fields = (
        'member__member_name',
    )

    list_filter = ('library',("datetime", DateRangeFilterBuilder()), 'datetime')

    '''
    Reports -
    R2 - Generate Gender wise report of members
    '''
    @admin.action(description="R2 - Generate Gender wise report of members")
    def generate_r2(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R2.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        cursor = connection.cursor()
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        with connection.cursor() as cursor:
            query = f"SELECT * FROM slots_slot where library = '{library}' and datetime >= '{start_day} 00:00:00' and datetime <= '{end_day} 23:00:00'"
            print(query)
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM members_member")
            columns = [col[0] for col in cursor.description]
            member_results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        member_gender_map = {}

        for row in member_results:
            member_gender_map[row['member_id']] = row['gender']

        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))

        output = {}

        for row in results:
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    mgender = member_gender_map[mid]
                    if mgender in output:
                        output[mgender] += 1
                    else:
                        output[mgender] = 1

        fieldnames = ["Gender", "Count of members"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in output.items():
            writer.writerow([k, v])
        return response
    
    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in ['generate_member_count_for_duration', 'generate_r2']:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                post.update({ACTION_CHECKBOX_NAME: str(Slot.objects.first().id)})
                request._set_post(post)
        return super(SlotAdmin, self).changelist_view(request, extra_context)

    actions = (
        'generate_r2',
    )

admin.site.register(Slot, SlotAdmin)
