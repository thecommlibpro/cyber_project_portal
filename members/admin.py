from django.contrib import admin
from .models import Member
import csv
from django.contrib.admin.helpers import ActionForm, AdminForm
from django import forms
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from datetime import datetime, date
 
def calculate_age(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) <
         (birthDate.month, birthDate.day))
    return age

class DataImport(ActionForm):
    
    file = forms.FileField(required=False)

class MemberAdmin(admin.ModelAdmin):
    
    action_form = DataImport

    @admin.action(description="Import Members from file")
    def import_members(modeladmin, request, queryset):
        ascii_file = request.FILES["file"]
        csv_string = ascii_file.file.read().decode('ascii')
        reader = csv.reader(csv_string.split('\n'), delimiter=';')
        for row in reader:
            if len(row) != 0 and row[0] != "cardnumber":
                input_data = Member()
                input_data.member_id = row[0]
                input_data.member_name = row[1]
                input_data.gender = Member.Gender(row[2])
                if row[3] != '':
                    dob = datetime.strptime(row[3], "%Y-%m-%d").date()
                    input_data.age = calculate_age(dob)
                else:
                    input_data.age = 0
                input_data.save()

    actions = (
        'import_members',
    )
    change_list_template = "slots/admin_form.html"
    list_display = ("member_id", "member_name", "gender", "age", )
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
                    post.update({ACTION_CHECKBOX_NAME: str(u.member_id)})
                request._set_post(post)
        return super(MemberAdmin, self).changelist_view(request, extra_context)

admin.site.register(Member, MemberAdmin)