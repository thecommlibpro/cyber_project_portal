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
    R1 - Generate Gender wise report of UNIQUE members
    R2 - Generate Gender wise report of members
    R3 - Generate Gender and Age wise report of members
    R4 - Generate Gender wise report of Most/Least frequent user
    R7 - Generate list of every member who took the slot
    '''
    @admin.action(description="R1 - Generate Gender wise report of UNIQUE members")
    def generate_r1(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R1.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)
        member_results = get_member_results()
        member_gender_map = {}

        for row in member_results:
            member_gender_map[row['member_id']] = row['gender']

        output = {}

        mid_set = set()

        for row in results:
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid and mid not in mid_set:
                    mgender = member_gender_map[mid]
                    if mgender in output:
                        output[mgender] += 1
                    else:
                        output[mgender] = 1
                mid_set.add(mid)

        fieldnames = ["Gender", "Count of members"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in output.items():
            writer.writerow([k, v])
        return response
    
    @admin.action(description="R2 - Generate Gender wise report of members")
    def generate_r2(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R2.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)
        member_results = get_member_results()
        member_gender_map = {}

        for row in member_results:
            member_gender_map[row['member_id']] = row['gender']

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
    
    @admin.action(description="R3 - Generate Gender and Age wise report of members")
    def generate_r3(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R3.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)
        member_results = get_member_results()
        member_gender_map = {}

        for row in member_results:
            age = row['age']
            if age >= 18:
                age = '18+'
            else:
                age = '11-18'
            member_gender_map[row['member_id']] = (row['gender'], age)

        output = {}

        for row in results:
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    mgender_age = member_gender_map[mid]
                    if mgender_age in output:
                        output[mgender_age] += 1
                    else:
                        output[mgender_age] = 1

        fieldnames = ["Gender", "Age group", "Count of members"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in output.items():
            print(k[1])
            writer.writerow([k[0], k[1], v])
        return response
    
    @admin.action(description="R4 - Generate Gender wise report of Most/Least frequent user")
    def generate_r4(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R4.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)
        member_results = get_member_results()
        member_gender_map = {}
        member_name_map = {}

        for row in member_results:
            member_gender_map[row['member_id']] = row['gender']
            member_name_map[row['member_id']] = row['member_name']

        # DS: {"Male": {"id_1": 10, "id_8": 4}, "Female": {"id_4": 7}}
        output = {}

        for row in results:
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    mgender = member_gender_map[mid]
                    op_mgender = output.get(mgender)
                    if not op_mgender:
                        output[mgender] = {mid:1}
                    else:
                        if mid in op_mgender:
                            op_mgender[mid] += 1
                        else:
                            op_mgender[mid] = 1

        min_max_gender_map = {}

        for gender, mid_count_map in output.items():
            count_list = mid_count_map.values()
            mostf_count = max(count_list)
            leastf_count = min(count_list)
            min_max_gender_map[gender] = [None, None]
            for mid, mid_count in mid_count_map.items():
                if mid_count == mostf_count or mid_count == leastf_count:
                    if mid_count == mostf_count:
                        ind = 0
                    else:
                        ind = 1
                    mname = member_name_map[mid].replace(" ", "-")
                    mid_mname = f"{mid}-{mname}"
                    if not min_max_gender_map[gender][ind]:
                        min_max_gender_map[gender][ind] = mid_mname
                    else:
                        min_max_gender_map[gender][ind] += f" | {mid_mname}"
        fieldnames = ["Gender", "Most frequent member", "Least frequent member"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in min_max_gender_map.items():
            writer.writerow([k, v[0], v[1]])
        return response
    
    @admin.action(description="R7 - Generate list of every member who took the slot")
    def generate_r7(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R7.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)
        member_results = get_member_results()
        member_gender_map = {}

        for row in member_results:
            member_gender_map[row['member_id']] = (row['member_name'], row['gender'], row['age'])

        output = {}

        for row in results:
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    member_info = member_gender_map[mid]
                    if mid not in output:
                        output[mid] = member_info

        fieldnames = ["Member ID", "Member Name", "Gender", "Age"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in output.items():
            writer.writerow([k, v[0], v[1], v[2]])
        return response
    
    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in ['generate_r1', 'generate_r2', 'generate_r3', 'generate_r4', 'generate_r7']:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                post.update({ACTION_CHECKBOX_NAME: str(Slot.objects.first().id)})
                request._set_post(post)
        return super(SlotAdmin, self).changelist_view(request, extra_context)

    actions = (
        'generate_r1',
        'generate_r2',
        'generate_r3',
        'generate_r4',
        'generate_r7',
    )

admin.site.register(Slot, SlotAdmin)
