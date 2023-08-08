from slots.models import LibraryNames, Slot, Member, LaptopCategories
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.contrib import messages

def generate_slots_for_a_month():
    today_day = today().date()
    month_end_day = today_day + relativedelta(days=30)

    while today_day < month_end_day:
        if today_day.weekday() < 5:
            start_time = "10:00 am"
            end_time = "6:00 pm"
        else:
            start_time = "1:00 pm"
            end_time = "9:00 pm"
        for library in LibraryNames.values:
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

def check_if_male_member_enrolled_consecutive(request):
    member_id = request.POST["member"]
    member_gender = Member.objects.filter(member_id=member_id)[0].gender
    slot_date = parse(request.POST["datetime_0"]).date()
    prev_date = slot_date - relativedelta(days=1)
    day = None
    if member_gender == Member.Gender.male:
        for obj in Slot.objects.filter(member=member_id):
            if prev_date == obj.datetime.date():
                day = "yesterday"
            elif slot_date == obj.datetime.date():
                day = "today"

    if day:
        messages.add_message(request=request, level=messages.WARNING, message='This member has used the slot ' + day)