from datetime import date
from typing import Optional

from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta


def calculate_age(dob) -> Optional[int]:
    birth_day = date_parse(dob)
    return relativedelta(date.today(), birth_day).years
