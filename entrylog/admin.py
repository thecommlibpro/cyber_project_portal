import csv

from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm, ACTION_CHECKBOX_NAME
from django.contrib.admin.widgets import AdminDateWidget
from django.http import HttpResponse
from rangefilter.filters import DateRangeFilterBuilder

from slots.models import LibraryNames
from .forms import LogAdminForm
from .models import EntryLog
from .reports import get_age_wise_unique_visitors, get_gender_wise_unique_visitors, get_footfall, get_first_timers


class EntryLogActionForm(ActionForm):
    library = forms.ChoiceField(choices=[('', '---')] + LibraryNames.choices, required=False)
    start_day = forms.DateField(widget=AdminDateWidget, required=False)
    end_day = forms.DateField(widget=AdminDateWidget, required=False)


class EntryLogAdmin(admin.ModelAdmin):
    form = LogAdminForm
    action_form = EntryLogActionForm
    list_display = (
        'library_location',
        'get_member_id',
        'member_name',
        'entered_date',
        'entered_time',
        'get_member_gender',
        'get_member_age'
    )
    list_display_links = (
        'get_member_id',
        'member_name',
    )
    list_filter = (
        'library',
        ('entered_date', DateRangeFilterBuilder('Log date')),
        'entered_date',
        'member__gender',
        'member__age',
    )
    search_fields = (
        'member__member_id',
        'member__member_name',
    )
    actions = [
        'generate_l1',
        'generate_l2',
        'generate_l3',
        'generate_l4',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('member')

    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and 'generate_l' in request.POST['action']:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                post.update({ACTION_CHECKBOX_NAME: str(EntryLog.objects.first().id)})
                request._set_post(post)

        return super().changelist_view(request, extra_context)

    def member_name(self, entry_log):
        return entry_log.member_name

    member_name.short_description = 'Member Name'
    member_name.admin_order_field = 'member__member_name'

    def get_member_id(self, entry_log):
        return entry_log.member.member_id

    get_member_id.short_description = 'Member ID'
    get_member_id.admin_order_field = 'member__member_id'

    def get_member_gender(self, entry_log):
        return entry_log.member.gender

    get_member_gender.short_description = 'Gender'
    get_member_gender.admin_order_field = 'member__gender'

    def get_member_age(self, entry_log):
        return entry_log.member.age

    get_member_age.short_description = 'Age'
    get_member_age.admin_order_field = 'member__age'

    @admin.action(description="L1 - Generate age wise report")
    def generate_l1(modeladmin, request, queryset):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        results, fieldnames = get_age_wise_unique_visitors(library, start_day, end_day)
        suffix = modeladmin._get_report_suffix(library, start_day, end_day)

        return modeladmin._generate_report_csv('L1' + suffix, results, fieldnames)

    @admin.action(description="L2 - Generate gender wise report")
    def generate_l2(modeladmin, request, queryset):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        results, fieldnames = get_gender_wise_unique_visitors(library, start_day, end_day)
        suffix = modeladmin._get_report_suffix(library, start_day, end_day)

        return modeladmin._generate_report_csv('L2' + suffix, results, fieldnames)

    @admin.action(description="L3 - Generate age + gender wise report of footfall")
    def generate_l3(modeladmin, request, queryset):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        results, fieldnames = get_footfall(library, start_day, end_day)
        suffix = modeladmin._get_report_suffix(library, start_day, end_day)

        return modeladmin._generate_report_csv('L3' + suffix, results, fieldnames)

    @admin.action(description="L4 - Generate first timers report")
    def generate_l4(modeladmin, request, queryset):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        results, fieldnames = get_first_timers(library, start_day, end_day)
        suffix = modeladmin._get_report_suffix(library, start_day, end_day)

        return modeladmin._generate_report_csv('L4' + suffix, results, fieldnames)

    @staticmethod
    def _get_report_suffix(library: str, start: str, end: str):
        suffix = f" - {library.split('-')[1]}" if library else "- All locations"
        suffix += " from " + (start or "(start)")
        suffix += " to " + (end or "(now)")
        return suffix

    @staticmethod
    def _generate_report_csv(report_name, results: list[dict], fieldnames=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={report_name}.csv'

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for row_dict in results:
            writer.writerow(row_dict)

        return response


admin.site.register(EntryLog, EntryLogAdmin)
