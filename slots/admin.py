from typing import Any
from django.contrib import admin
from .models import Slot
from django.contrib import messages
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from rangefilter.filters import DateRangeFilterBuilder, DateTimeRangeFilterBuilder, NumericRangeFilterBuilder

from .models import LibraryNames, SlotTimes
from .utils import generate_slots as generate_util, generate_slots_for_a_month, check_if_male_member_enrolled_consecutive
from .forms import SlotForm

class GenerateSlotForm(ActionForm):
    library = forms.ChoiceField(choices=LibraryNames.choices, required=False)
    start_time = forms.ChoiceField(choices=SlotTimes.choices, required=False)
    end_time = forms.ChoiceField(choices=SlotTimes.choices, required=False)
    date = forms.DateField(widget=AdminDateWidget, required=False)

class SlotAdmin(admin.ModelAdmin):

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        check_if_male_member_enrolled_consecutive(request)
        return super().save_model(request, obj, form, change)

    form = SlotForm
    action_form = GenerateSlotForm
    list_display = (
        'get_time',
        'member',
        # 'get_member_name',
        'get_member_gender',
    )

    @admin.display(ordering='-datetime', description='Slot time')
    def get_time(self, obj):
        return obj.datetime.strftime("%I:%M%p")

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

    @admin.action(description="Generate slots for the month")
    def generate_slots_for_month(modeladmin, request, queryset):
        generate_slots_for_a_month()

    @admin.action(description="Generate slots for the day")
    def generate_slots(modeladmin, request, queryset):
        request_json = request.POST
        start_time = request_json["start_time"]
        end_time = request_json["end_time"]
        date = request_json["date"]
        library = request_json["library"]

        print(library, date, start_time, end_time)
        generate_util(library, date, start_time, end_time)
    
    # This is for not having to select any existing slot in case of generating slots
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] in ['generate_slots', 'generate_slots_for_month']:
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Slot.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super(SlotAdmin, self).changelist_view(request, extra_context)

    
    actions = (
        'generate_slots', 'generate_slots_for_month'
    )

admin.site.register(Slot, SlotAdmin)
