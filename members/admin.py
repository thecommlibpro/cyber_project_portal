import logging

from django.contrib import admin

from entrylog.models import EntryLog
from .models import Member, Gender
import csv
from django.contrib.admin.helpers import ActionForm, AdminForm
from django import forms
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from datetime import datetime, date
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta

from utils import calculate_age


class DataImport(ActionForm):

    file = forms.FileField(required=False)


class EntryLogInline(admin.TabularInline):
    model = EntryLog
    extra = 0
    show_full_result_count = True
    ordering = [
        '-entered_date',
        '-entered_time',
    ]
    exclude = [
        'library',
    ]


class MemberAdmin(admin.ModelAdmin):
    action_form = DataImport
    inlines = [
        EntryLogInline,
    ]

    @admin.action(description="Import Members from file")
    def import_members(modeladmin, request, queryset):
        csv_file = request.FILES["file"].read().decode('utf-8').splitlines()
        reader = csv.DictReader(
            csv_file,
            fieldnames=[
                'borrower_number',
                'card_number',
                'first_name',
                'last_name',
                'birth_date',
                'library_code',
                'enrolled_in_cyber_project',
                'footfall_date',
                'gender',
            ],
            delimiter=';',
            quotechar='"',
        )

        _ = next(reader)

        count = 0

        for row in reader:
            try:
                card_number = row['card_number'].strip().upper()
                member = Member.objects.filter(member_id=card_number).first() or Member.objects.create(member_id=card_number)

                member.member_name = f"{row['first_name'].strip()} {row['last_name'].strip()}"
                member.gender = Gender(row['gender'].strip()) if row['gender'] else None
                member.dob = date_parse(row['birth_date']) if row['birth_date'] else None
                member.age = calculate_age(row['birth_date']) if row['birth_date'] else 0
                member.first_login_at = member.first_login_at or (date_parse(row['footfall_date']) if row['footfall_date'] else None)
                member.cyber_project_enabled = row['enrolled_in_cyber_project'].strip() == 'Yes'

                member.save()

                count += 1
                logging.info(f"member count: {count}")
            except Exception as e:
                modeladmin.message_user(request, f"Error importing row {row}: {e}")


    actions = (
        'import_members',
    )
    change_list_template = "slots/admin_form.html"
    list_display = (
        "member_id",
        "member_name",
        "gender",
        "age",
        "cyber_project_enabled",
        "first_login_at",
    )
    list_filter = (
        'cyber_project_enabled',
        'gender',
        'age',
    )
    search_fields = (
        'member_name',
        'member_id',
        'gender',
    )

    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in ['import_members']:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Member.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.uid)})
                request._set_post(post)
        return super(MemberAdmin, self).changelist_view(request, extra_context)

admin.site.register(Member, MemberAdmin)