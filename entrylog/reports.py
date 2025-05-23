from collections import defaultdict
from datetime import datetime

from django.db.models import Count, F, Min, Max, Q

from entrylog.models import EntryLog
from members.models import Member, Gender
from slots.models import LibraryNames


def get_age_wise_unique_visitors(library=None, start=None, end=None):
    """
    Returns data about age group -> count of members who have visited the library at least once in the time period.
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
    Returns data about gender -> count of members who have visited the library at least once in the time period.
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
    Get footfall data. It counts how many members have visited the library in a given time period.

    Each entry is counted for all the members in the library. If a member visits multiple times in the given
    period, it is counted multiple times.

    The report is organized by gender and age group. Each row contains the count of entries of a certain age
    group and gender combination.
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


def get_first_timers(library=None, start=None, end=None):
    """
    Return list of members who have come to the library for the first time in that time period.

    Example: If a member visits for the first time in April and then visited in subsequent months, they will be included
    only in the report for April, not in May or June.
    """
    start = start or EntryLog.DEFAULT_START_DATE
    end = end or datetime.now()

    library_filter = Q(member_logs__library=library) if library else None
    members = Member.objects.annotate(
        log_count=Count('member_logs'),
    ).exclude(
        log_count=0,
    ).annotate(
        first_login=Min('member_logs__entered_date', filter=library_filter),
    ).filter(
        first_login__range=(start, end),
    )

    results = []

    for member in members:
        results.append({
            'Member ID': member.member_id,
            'Name': member.member_name,
            'Gender': member.gender,
            'Age': member.age,
            'First Login': member.first_login,
            'Log Count': member.log_count,
        })

    return (
        results,
        [
            'Member ID',
            'Name',
            'Gender',
            'Age',
            'First Login',
            'Log Count',
        ]
    )


def get_most_frequent_users(library=None, start=None, end=None):
    """
    Get details about all members who have visited the library at least once in the given time period, with their
    details and the number of times they have visited the library in that time period.
    """
    filters = Q(
        member_logs__entered_date__range=(start or EntryLog.DEFAULT_START_DATE, end or datetime.now()),
    )

    if library:
        filters = filters & Q(member_logs__library=library)

    members = Member.objects.annotate(
        entry_count=Count('member_logs', filter=filters)
    ).exclude(entry_count=0).order_by('-entry_count')

    results = []

    for member in members:
        results.append({
            'Member ID': member.member_id,
            'Name': member.member_name,
            'Age': member.age,
            'Gender': member.gender,
            'Entry Count': member.entry_count,
        })

    return (
        results,
        [
            'Member ID',
            'Name',
            'Age',
            'Gender',
            'Entry Count',
        ]
    )


def get_members_who_did_not_visit(library=None, start=None, end=None):
    """
    Return a list of members who have not visited the library in the given time period.
    """
    start = start or EntryLog.DEFAULT_START_DATE
    end = end or datetime.now()
    library_filter = Q(member_logs__library=library) if library else Q()
    membership_filter = Q(member_id__istartswith=LibraryNames.get_library_code(library)) if library else Q()

    members = Member.objects.filter(membership_filter).exclude(
        Q(member_logs__entered_date__range=(start, end)) & library_filter,
    ).annotate(
        last_visit=Max('member_logs__entered_date'),
    )

    results = []

    for member in members:
        results.append({
            'Member ID': member.member_id,
            'Name': member.member_name,
            'Age': member.age,
            'Gender': member.gender,
            'Last Visit': member.last_visit,
        })

    return (
        results,
        [
            'Member ID',
            'Name',
            'Age',
            'Gender',
            'Last Visit',
        ],
    )
