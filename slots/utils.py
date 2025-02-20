from members.models import Gender
from slots.models import LibraryNames, Slot, Member, LaptopCategories
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.contrib import messages
from django.db import connection
from django import forms

def generate_slots_for_a_month():
    today_day = today().date()
    month_end_day = today_day + relativedelta(days=30)

    while today_day < month_end_day:
        for library in LibraryNames.values:
            # if library == "The Community Library Project - Khirki":
            start_time = "12:00 pm"
            end_time = "8:00 pm"
            # for laptop in LaptopCategories.values:
            generate_slots(library, str(today_day), start_time, end_time)
        today_day += relativedelta(days=1)

def generate_slots(library, date, start_time, end_time):
    # The Community Library Project - Khirki 2023-07-29 8:00 am 8:00 am

    library = LibraryNames(library)

    start_time = parse(date + ' ' + start_time)
    end_time = parse(date + ' ' + end_time)

    while start_time < end_time:
        Slot.objects.create(
            library=library,
            datetime=start_time
        )

        start_time += relativedelta(minutes=60)
'''
Rules for slots
'''

def check_if_male_member_enrolled_consecutive(request):
    member_id = request.POST["member"]
    member_gender = Member.objects.filter(member_id=member_id)[0].gender
    slot_date = parse(request.POST["datetime_0"]).date()
    prev_date = slot_date - relativedelta(days=1)
    day = None
    if member_gender == Gender.male:
        for obj in Slot.objects.filter(member=member_id):
            if prev_date == obj.datetime.date():
                day = "yesterday"
            elif slot_date == obj.datetime.date():
                day = "today"

    if day:
        messages.add_message(request=request, level=messages.WARNING, message='This member has used the slot ' + day)

def check_time_slot_for_age_group(member_id, slot_datetime, library):
    if library != LibraryNames.TCLP_04:
        return

    member_age = Member.objects.filter(member_id=member_id)[0].age
    if member_age < 16:
        if slot_time := slot_datetime.time():
            if slot_time < parse("12:00 pm").time() or slot_time > parse("4:30 pm").time():
                raise forms.ValidationError(
                    f"Member {member_id} is below 16 years and can only take slots from 12:00 pm to 5:30 pm")
    else:
        if slot_time := slot_datetime.time():
            if slot_time < parse("5:00 pm").time() or slot_time > parse("8:00 pm").time():
                raise forms.ValidationError(
                    f"Member {member_id} is above 16 years and can only take slots from 6:00 pm to 8:00 pm")

def get_member_results():
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM members_member")
    columns = [col[0] for col in cursor.description]
    member_results = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
    return member_results

def get_slot_results(library, start_day, end_day):
    """
    Return a list of dict objects of all the slots filtered by the library and date range.
    """
    slots = Slot.objects.filter(datetime__range=(start_day, end_day))

    if library:
        slots = slots.filter(library=library)

    results = []
    field_names = Slot._meta.fields

    for slot in slots:
        result = dict()
        for field in field_names:
            if 'laptop_' in field.name:
                result[field.name + '_id'] = getattr(getattr(slot, field.name), 'member_id', None)
            else:
                result[field.name] = getattr(slot, field.name)

        results.append(result)

    return results
