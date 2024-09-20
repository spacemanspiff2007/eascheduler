from datetime import date as dt_date
from datetime import datetime as dt_datetime

from whenever import Date, Instant, SystemDateTime

from eascheduler.builder.helper import HINT_INSTANT, get_instant
from eascheduler.producers.prod_filter import is_holiday as _is_holiday
from eascheduler.producers.prod_sun import get_azimuth_and_elevation


def get_sun_position(instant: HINT_INSTANT) -> tuple[float, float]:
    """Return the sun position (azimuth and elevation) at a given instant.

    :param instant: instant to get the sun position at or None for now
    :return: azimuth and elevation of the sun at the specified instant
    """
    return get_azimuth_and_elevation(get_instant(instant))


def is_holiday(date: dt_date | dt_datetime | str | None | Date | SystemDateTime | Instant) -> bool:
    """Check if a given date is a holiday.

    :param date: Date to check or None for today
    :return: True if the date is a holiday, False otherwise
    """

    match date:
        case dt_date():
            value = date
        case dt_datetime():
            value = date.date()
        case str():
            value = Date.parse_common_iso(date).py_date()
        case None:
            value = SystemDateTime.now().date().py_date()

        case Date():
            value = date.py_date()
        case SystemDateTime():
            value = date.date().py_date()
        case Instant():
            value = date.to_system_tz().date().py_date()

        case _:
            raise TypeError()

    return _is_holiday(value)
