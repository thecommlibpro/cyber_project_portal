from slots.models import LibraryNames, Slot
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


def generate_slots(library, date, start_time, end_time):
    # The Community Library Project - Khirki 2023-07-29 8:00 am 8:00 am
    library = LibraryNames(library)
    start_time = parse(date + ' ' + start_time)
    end_time = parse(date + ' ' + end_time)

    while start_time < end_time:
        Slot.objects.create(
            library=library,
            datetime=start_time,
        )

        start_time += relativedelta(minutes=30)

