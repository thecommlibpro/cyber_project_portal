import logging

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from members.models import Member


def update_koha(member_id):
    member = Member.objects.get(member_id=member_id)
    first_visit_date = member.member_logs.order_by('entered_date').first().entered_date.isoformat()
    last_visit_date = member.member_logs.order_by('-entered_date').first().entered_date.isoformat()

    auth = HTTPBasicAuth(settings.KOHA_API['USERNAME'], settings.KOHA_API['PASSWORD'])
    base_url = settings.KOHA_API['BASE_URL']

    response = requests.get(
        f'{base_url}/patrons/?cardnumber={member_id}',
        headers={
            'x-koha-embed': 'extended_attributes',
        },
        auth=auth,
    )

    member_data = response.json()[0]
    patron_id = member_data["patron_id"]

    for attribute in member_data['extended_attributes']:
        member_data[attribute['type']] = attribute

    first_visit_date = member_data.get('FIRST_VISIT', {}).get('value') or first_visit_date
    last_visit_date = member_data.get('LAST_VISIT', {}).get('value') or last_visit_date

    if member_data.get('FIRST_VISIT'):
        response = requests.patch(
            f'{base_url}/patrons/{patron_id}/extended_attributes/{member_data["FIRST_VISIT"]["extended_attribute_id"]}',
            auth=auth,
            json={
                'value': first_visit_date,
            },
        )

    else:
        response = requests.post(
            f'{base_url}/patrons/{patron_id}/extended_attributes',
            auth=auth,
            json={
                'type': 'FIRST_VISIT',
                'value': first_visit_date,
            }
        )

    if not response.ok:
        logging.error(f'Failed to update first visit {member_id}: {response.status_code}')

    if member_data.get('LAST_VISIT'):
        response = requests.patch(
            f'{base_url}/patrons/{patron_id}/extended_attributes/{member_data["LAST_VISIT"]["extended_attribute_id"]}',
            auth=auth,
            json={
                'value': last_visit_date,
            }
        )
    else:
        response = requests.post(
            f'{base_url}/patrons/{patron_id}/extended_attributes',
            auth=auth,
            json={
                'type': 'LAST_VISIT',
                'value': last_visit_date,
            }
        )

    if not response.ok:
        logging.error(f'Failed to update last visit {member_id}: {response.status_code}')

    logging.info(f"Updated visits {first_visit_date}, {last_visit_date} on Koha for member {member_id}")
