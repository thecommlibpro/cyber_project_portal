from collections import defaultdict
from typing import Any

from dateutil.rrule import rrule, MONTHLY
from django.db.models import Count, Q, Sum, Value, F, Prefetch
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
        'wrapped_field_laptop_adult_common_1',
        'wrapped_field_laptop_adult_non_male',
    )
    readonly_fields = (
        'library',
        'datetime',
    )
    fieldsets = (
        (None, {
            'fields': (
                'library',
                'datetime',
            ),
        }),
        ('Laptops', {
            'fields': list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()])),
        }),
    )

    wrapped_field_laptop_common_1 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_common_1) if x.laptop_common_1 else "", 'Laptop for All - 1', 'Laptop for All - 1')
    wrapped_field_laptop_common_2 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_common_2) if x.laptop_common_2 else "", "Laptop for All - 2", "Laptop for All - 2")
    wrapped_field_laptop_non_male_1 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_non_male_1) if x.laptop_non_male_1 else "", "Laptop for Girls, T, NB - 1", "Laptop for Girls, T, NB - 1")
    wrapped_field_laptop_non_male_2 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_non_male_2) if x.laptop_non_male_2 else "", "Laptop for Girls, T, NB - 2", "Laptop for Girls, T, NB - 2")
    wrapped_field_laptop_education = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_education) if x.laptop_education else "", "Laptop for Education", "Laptop for Education")
    wrapped_field_laptop_disability = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_disability) if x.laptop_disability else "", "Laptop for P w Disabilities", "Laptop for P w Disabilities")
    wrapped_field_laptop_adult_common_1 = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_adult_common_1) if x.laptop_adult_common_1 else "", "Laptop for adults - Common", "Laptop for adults - Common")
    wrapped_field_laptop_adult_non_male = easy.SimpleAdminField(lambda x: linebreaksbr(x.laptop_adult_common_1) if x.laptop_adult_common_1 else "", "Laptop for adults - T, NB, and Women", "Laptop for adults - T, NB, and Women")

    def has_delete_permission(self, request, obj=None):
        return False

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
        'laptop_common_1__member_id',
        'laptop_common_1__member_name',
        'laptop_common_2__member_id',
        'laptop_common_2__member_name',
        'laptop_non_male_1__member_id',
        'laptop_non_male_1__member_name',
        'laptop_non_male_2__member_id',
        'laptop_non_male_2__member_name',
        'laptop_education__member_id',
        'laptop_education__member_name',
        'laptop_disability__member_id',
        'laptop_disability__member_name',
        'laptop_adult_common_1__member_id',
        'laptop_adult_common_1__member_name',
        'laptop_adult_non_male__member_id',
        'laptop_adult_non_male__member_name',
    )

    list_filter = ('library',("datetime", DateRangeFilterBuilder()), 'datetime')

    '''
    Reports -
    R1 - Generate Gender wise report of UNIQUE members
    R2 - Generate Gender wise report of members
    R3 - Generate Gender and Age wise report of members
    R4 - Generate Gender wise report of Most/Least frequent user
    R5 - Generate Most/Least popular time of the day
    R6 - Generate Gender and age wise Most/Least popular time of the day
    R7 - Generate list of every member who took the slot
    R8 - Generate slot count for all members (13yo - 16yo)
    R9 - Generate gender-wise education slots report
    R10 - Generate monthly usage report
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
                age = '18+ years'
            else:
                age = '11-18 years'
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
            if min_max_gender_map[gender][0]:
                min_max_gender_map[gender][0] = f"[{str(mostf_count)}] " + min_max_gender_map[gender][0]
            if min_max_gender_map[gender][1]:
                min_max_gender_map[gender][1] = f"[{str(leastf_count)}] " + min_max_gender_map[gender][1]
        fieldnames = ["Gender", "Most frequent member", "Least frequent member"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in min_max_gender_map.items():
            writer.writerow([k, v[0], v[1]])
        return response

    @admin.action(description="R5 - Generate Most/Least popular time of the day")
    def generate_r5(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R5.csv'
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]
        laptop_list = list(filter(lambda x: x.startswith("laptop"), [x.name for x in Slot._meta.get_fields()]))
        results = get_slot_results(library, start_day, end_day)

        slot_freq = {}

        for row in results:
            slot_time = row["datetime"].strftime("%I %p")
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    if slot_time in slot_freq:
                        slot_freq[slot_time] += 1
                    else:
                        slot_freq[slot_time] = 1

        most_slot_freq = " | ".join([k for (k,v) in slot_freq.items() if v == max(slot_freq.values())])
        least_slot_freq = " | ".join([k for (k,v) in slot_freq.items() if v == min(slot_freq.values())])

        fieldnames = ["Most popular time", "Least popular time"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        writer.writerow([most_slot_freq, least_slot_freq])
        return response

    @admin.action(description="R6 - Generate Gender and Age wise Most/Least popular time of the day")
    def generate_r6(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R6.csv'
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
                age = '18+ years'
            else:
                age = '11-18 years'
            member_gender_map[row['member_id']] = (row['gender'], age)

        # {("Male", "11-18 years"): {"11 am": 4, "2pm": 5, "3pm":4}, ("Female", "11-18 years"): {"11 am": 2, "2pm": 5, "3pm":4}}
        slot_freq = {}

        for row in results:
            slot_time = row["datetime"].strftime("%I %p")
            for laptop in laptop_list:
                mid = row[f"{laptop}_id"]
                if mid:
                    minfo = member_gender_map[mid]
                    mslotfreq = slot_freq.get(minfo)
                    if mslotfreq:
                        if slot_time in mslotfreq:
                            mslotfreq[slot_time] += 1
                        else:
                            mslotfreq[slot_time] = 1
                    else:
                        slot_freq[minfo] = {slot_time: 1}

        for group, group_slot_freq in slot_freq.items():
            most_group_freq = " | ".join([k for (k,v) in group_slot_freq.items() if v == max(group_slot_freq.values())])
            least_group_freq = " | ".join([k for (k,v) in group_slot_freq.items() if v == min(group_slot_freq.values())])
            slot_freq[group] = (most_group_freq, least_group_freq)

        fieldnames = ["Gender", "Age group", "Most popular time", "Least popular time"]
        writer = csv.writer(response)
        writer.writerow(fieldnames)
        for k,v in slot_freq.items():
            writer.writerow([k[0], k[1], v[0], v[1]])
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

    @admin.action(description="R8 - Generate slot count for all members (13yo - 16yo)")
    def generate_r8(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R8.csv'

        start_day = request.POST["start_day"]
        end_day = request.POST["end_day"]
        library = LibraryNames(request.POST.get('library'))

        slots = get_slot_results(library, start_day, end_day)
        members = Member.objects.filter(age__isnull=False)

        member_map = {
            member.member_id: {
                'member_id': member.member_id,
                'member_name': member.member_name,
                'gender': member.gender,
                'age': member.age,
                'laptop_common_1': 0,
                'laptop_common_2': 0,
                'laptop_non_male_1': 0,
                'laptop_non_male_2': 0,
                'laptop_education': 0,
                'laptop_disability': 0,
            } for member in members
        }
        member_map[None] = {
            'laptop_common_1': 0,
            'laptop_common_2': 0,
            'laptop_non_male_1': 0,
            'laptop_non_male_2': 0,
            'laptop_education': 0,
            'laptop_disability': 0,
        }

        for slot in slots:
            member_map[slot['laptop_common_1_id']]['laptop_common_1'] += 1
            member_map[slot['laptop_common_2_id']]['laptop_common_2'] += 1
            member_map[slot['laptop_non_male_1_id']]['laptop_non_male_1'] += 1
            member_map[slot['laptop_non_male_2_id']]['laptop_non_male_2'] += 1
            member_map[slot['laptop_education_id']]['laptop_education'] += 1
            member_map[slot['laptop_disability_id']]['laptop_disability'] += 1

        del member_map[None]

        for member in member_map.values():
            member['total'] = sum([member[k] if k.startswith('laptop_') else 0 for k in member.keys()])

        # convert list of values to csv file
        fieldnames = [
            "Member ID",
            "Member Name",
            "Gender",
            "Age",
            "Laptop Common 1 Count",
            "Laptop Common 2 Count",
            "Laptop Non Male 1 Count",
            "Laptop Non Mail 2 Count",
            "Laptop Education Count",
            "Laptop Disability Count",
            "Total",
        ]

        writer = csv.writer(response)
        writer.writerow(fieldnames)

        for member in sorted(member_map.values(), key=lambda x: x['total'], reverse=True):
            if member['age'] < 13 or member['age'] > 16:
                continue

            if member['total'] == 0:
                continue

            writer.writerow([
                member['member_id'],
                member['member_name'],
                member['gender'],
                member['age'],
                member['laptop_common_1'],
                member['laptop_common_2'],
                member['laptop_non_male_1'],
                member['laptop_non_male_2'],
                member['laptop_education'],
                member['laptop_disability'],
                member['total'],
            ])

        return response

    @admin.action(description="R9 - Generate gender-wise education slots report")
    def generate_r9(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R9.csv'
        library = LibraryNames(request.POST.get('library'))

        start_day = request.POST["start_day"]
        end_day = request.POST["end_day"]

        date_range = (parse(start_day), parse(end_day))

        member_laptop_counts = Member.objects.annotate(
            count=Count(
                'laptop_education',
                filter=Q(laptop_education__library=library, laptop_education__datetime__range=date_range),
            )
        )
        writer = csv.writer(response)

        gender_counts = defaultdict(int)

        for member in member_laptop_counts:
            gender_counts[member.gender] += member.count

        writer.writerow(["Gender", "Slots"])

        for gender in gender_counts:
            writer.writerow((gender, gender_counts[gender]))

        return response

    @admin.action(description="R10 - Generate monthly usage report")
    def generate_r10(modeladmin, request, queryset):
        """Generate monthly usage report"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=R10.csv'

        library = request.POST.get('library')
        start_day, end_day = request.POST['start_day'], request.POST['end_day']

        months_list = [(dt.year, dt.month) for dt in rrule(MONTHLY, dtstart=parse(start_day), until=parse(end_day))]
        slots = Slot.objects.filter(datetime__range=(start_day, end_day))

        if library:
            slots = slots.filter(library=library)

        laptops = [f.name + '_id' for f in filter(lambda f: 'laptop_' in f.name, Slot._meta.fields)]

        members = Member.objects.all()
        member_map = defaultdict(lambda: defaultdict(None))

        # Prepare a mapping for slots with members
        slot_member_map = defaultdict(list)
        for slot in slots:
            for field in laptops:
                member_id = getattr(slot, field)
                if member_id:
                    slot_member_map[member_id].append(slot)

        for member in members:
            if member.pk not in slot_member_map:
                continue

            member_slots = slot_member_map[member.pk]
            total = 0

            for year, month in months_list:
                month_count = sum(
                    1 if slot.datetime.year == year and slot.datetime.month == month else 0
                    for slot in member_slots
                )
                member_map[member.member_id][f'{year}-{month}'] = month_count
                total += month_count

            member_map[member.member_id].update({
                'Member ID': member.member_id,
                'Name': member.member_name,
                'Age': member.age,
                'Gender': member.gender,
                'Total Slots': total,
            })

        fieldnames = [
            'Member ID', 'Name', 'Age', 'Gender', 'Total Slots',
        ] + [f'{year}-{month}' for year, month in months_list]

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(member_map.values())

        return response

    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and 'generate_r' in request.POST['action']:
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
        'generate_r5',
        'generate_r6',
        'generate_r7',
        'generate_r8',
        'generate_r9',
        'generate_r10',
    )

admin.site.register(Slot, SlotAdmin)
