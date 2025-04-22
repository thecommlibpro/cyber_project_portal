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
from .reports import (
    get_age_wise_unique_visitors,
    get_gender_wise_unique_visitors,
    get_footfall,
    get_first_timers,
    get_most_frequent_users, get_members_who_did_not_visit,
)


class EntryLogActionForm(ActionForm):
    library = forms.ChoiceField(choices=[('', 'All')] + LibraryNames.choices, required=False)
    start_day = forms.DateField(widget=AdminDateWidget, required=False)
    end_day = forms.DateField(widget=AdminDateWidget, required=False)


class EntryLogAdmin(admin.ModelAdmin):
    form = LogAdminForm
    action_form = EntryLogActionForm
    change_list_template = "admin/changelist.html"
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
        'generate_l5',
        'generate_l6',
    ]
    ordering = [
        '-entered_date',
        '-entered_time',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('member')

    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['reports_info'] = self._get_report_descriptions()

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

    @admin.action(description="L1 - Generate age wise UFF report")
    def generate_l1(modeladmin, request, queryset):
        return modeladmin._generate_report(request, queryset, 'L1')

    @admin.action(description="L2 - Generate gender wise UFF report")
    def generate_l2(modeladmin, request, queryset):
        return modeladmin._generate_report(request, queryset, 'L2')

    @admin.action(description="L3 - Generate age + gender wise report of member footfall")
    def generate_l3(modeladmin, request, queryset):
        return modeladmin._generate_report(request, queryset, 'L3')

    @admin.action(description="L4 - Generate first timers report")
    def generate_l4(modeladmin, request, queryset):
        return modeladmin._generate_report(request, queryset, 'L4')

    @admin.action(description="L5 - Generate most frequent users report")
    def generate_l5(modeladmin, request, queryset):
        return modeladmin._generate_report(request, queryset, 'L5')

    @admin.action(description="L6 - Generate non-visiting members report")
    def generate_l6(modeladmin, request, queryset):
        modeladmin.res
        return modeladmin._generate_report(request, queryset, 'L6')

    def _generate_report(modeladmin, request, queryset, report_name):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        report_map = {
            'L1': get_age_wise_unique_visitors,
            'L2': get_gender_wise_unique_visitors,
            'L3': get_footfall,
            'L4': get_first_timers,
            'L5': get_most_frequent_users,
            'L6': get_members_who_did_not_visit,
        }

        results, fieldnames = report_map[report_name](library, start_day, end_day)
        suffix = modeladmin._get_report_suffix(library, start_day, end_day)

        modeladmin.message_user(request, f"Report {report_name} generated successfully{suffix}")

        return modeladmin._generate_report_csv(report_name + suffix, results, fieldnames)

    @staticmethod
    def _get_report_suffix(library: str, start: str, end: str):
        suffix = f" - {library.split('-')[1]}" if library else " - All locations"
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

    def _get_report_descriptions(modeladmin):
        report_map = {
            'L1': ("Age wise UFF report", get_age_wise_unique_visitors),
            'L2': ("Gender wise UFF report", get_gender_wise_unique_visitors),
            'L3': ("Age + gender wise report of member footfall", get_footfall),
            'L4': ("First timers report", get_first_timers),
            'L5': ("Most frequent users report", get_most_frequent_users),
            'L6': ("Non-visiting members report", get_members_who_did_not_visit),
        }

        description = ""

        for report_name, (report_description, _) in report_map.items():
            description += f"<b>{report_name} - {report_description}</b><br />"
            description += f"<p>{report_map[report_name][1].__doc__.replace('\n', '<br />')}</p><br />"

        return description


admin.site.register(EntryLog, EntryLogAdmin)
