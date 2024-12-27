from collections import defaultdict
from datetime import datetime

from dateutil.parser import parse as date_parse
from django.db.models import Count, F

from entrylog.models import EntryLog
from members.models import Member, Gender


def get_age_wise_unique_visitors(library=None, start=None, end=None):
    """
    Returns a list of dicts, containing age -> count of members who have visited the library at least once.
    """
    entry_logs = EntryLog.filtered(library, start, end)
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
    entry_logs = EntryLog.filtered(library, start, end)
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


def get_footfall(library=None, start=None, end=None):
    """
    Returns a list of dicts, combining counts for age + gender combo.
    """
    age_map = {
        'CHILD': 0,
        'HEAD_START': 0,
        'LOWER': 0,
        'UPPER': 0,
        'ADULT': 0,
        'UNKNOWN': 0,
    }
    gender_map = {key: dict(**age_map) for key, _ in Gender.choices}
    gender_map['Unknown'] = dict(**age_map)
    values = EntryLog.filtered(library, start, end).values_list(
        'member__age',
        'member__gender',
    )

    for age, gender in values:
        if age is None:
            age_group = 'UNKNOWN'
        elif age < 4:
            age_group = 'CHILD'
        elif age < 6:
            age_group = 'HEAD_START'
        elif age < 12:
            age_group = 'LOWER'
        elif age < 18:
            age_group = 'UPPER'
        else:
            age_group = 'ADULT'

        gender_map[gender or 'Unknown'][age_group] += 1

    results = []

    for gender in gender_map:
        for age_group in gender_map[gender]:
            results.append(dict(
                Gender=gender,
                AgeGroup=age_group,
                Count=gender_map[gender][age_group],
            ))

    results.append(dict(
        Gender='All',
        AgeGroup='All',
        Count=values.count(),
    ))

    return (
        results,
        ['Gender', 'AgeGroup', 'Count'],
    )

