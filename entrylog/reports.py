from collections import defaultdict
from datetime import datetime

from dateutil.parser import parse as date_parse
from django.db.models import Count, F

from entrylog.models import EntryLog
from members.models import Member

DEFAULT_START_DATE = date_parse('2022-01-01')  # When daily logs started to be recorded


def get_age_wise_unique_visitors(library=None, start=None, end=None):
    """
    Returns a list of dicts, containing age -> count of members who have visited the library at least once.
    """
    start = start or DEFAULT_START_DATE
    end = end or datetime.today()
    entry_logs = EntryLog.objects.filter(
        entered_date__range=(start, end),
    )

    if library:
        entry_logs = entry_logs.filter(library=library)

    member_ids = entry_logs.values_list('member_id').distinct()

    age_map = defaultdict(int)
    age_range_map = {
        'CHILD': 0,
        'HEAD_START': 0,
        'LOWER': 0,
        'UPPER': 0,
        'ADULT': 0,
        'UNKNOWN': 0,
        'TOTAL': len(member_ids),
    }

    for member in Member.objects.filter(uid__in=member_ids):
        age = member.age
        if age is None:
            age_range_map['UNKNOWN'] += 1
        elif age < 4:
            age_range_map['CHILD'] += 1
        elif age < 6:
            age_range_map['HEAD_START'] += 1
        elif age < 12:
            age_range_map['LOWER'] += 1
        elif age < 18:
            age_range_map['UPPER'] += 1
        else:
            age_range_map['ADULT'] += 1

        age_map[age] += 1

    age_map_results = sorted(age_map.items())
    combined = [{'Age/Age Group': k, 'Count': v} for k, v in (list(age_range_map.items()) + list(age_map_results))]

    return combined, ['Age/Age Group', 'Count']


def get_gender_wise_unique_visitors(library=None, start=None, end=None):
    """
    Returns a list of dicts, containing gender -> count of members who have visited the library at least once.
    """
    start = start or DEFAULT_START_DATE
    end = end or datetime.today()
    entry_logs = EntryLog.objects.filter(
        entered_date__range=(start, end),
    )

    if library:
        entry_logs = entry_logs.filter(library=library)

    members = Member.objects.filter(uid__in=entry_logs.values_list('member_id')).distinct()

    values = members.values('gender').order_by('gender').annotate(
        Count=Count('gender'),
    ).annotate(Gender=F('gender')).values(
        'Gender', 'Count',
    )

    return (
        list(values) + [{'Gender': 'Total', 'Count': members.count()}],
        ['Gender', 'Count'],
    )
