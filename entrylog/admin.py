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
from .reports import get_age_wise_unique_visitors


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
    )
    list_display_links = (
        'get_member_id',
        'member_name',
    )
    list_filter = (
        'library',
        ('entered_date', DateRangeFilterBuilder('Log date')),
        'entered_date',
    )
    search_fields = (
        'member__member_id',
        'member__member_name',
    )
    actions = [
        'generate_l1',
    ]

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

    @admin.action(description="L1 - Generate age wise report of UNIQUE members")
    def generate_l1(modeladmin, request, queryset):
        request_json = dict(request.POST)
        library = request_json["library"][0]
        start_day = request_json["start_day"][0]
        end_day = request_json["end_day"][0]

        results, fieldnames = get_age_wise_unique_visitors(library, start_day, end_day)

        return modeladmin._generate_report_csv('L1', results, fieldnames)

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
