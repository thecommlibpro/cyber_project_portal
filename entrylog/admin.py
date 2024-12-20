from django.contrib import admin
from rangefilter.filters import DateRangeFilterBuilder

from .forms import LogAdminForm
from .models import EntryLog


class EntryLogAdmin(admin.ModelAdmin):
    form = LogAdminForm
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

    def member_name(self, entry_log):
        return entry_log.member_name

    member_name.short_description = 'Member Name'
    member_name.admin_order_field = 'member__member_name'

    def get_member_id(self, entry_log):
        return entry_log.member.member_id

    get_member_id.short_description = 'Member ID'
    get_member_id.admin_order_field = 'member__member_id'


admin.site.register(EntryLog, EntryLogAdmin)
