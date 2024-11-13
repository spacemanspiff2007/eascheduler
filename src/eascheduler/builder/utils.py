from datetime import date as dt_date
from typing import Literal, TypeVar, overload

from eascheduler.builder.helper import HINT_DATE, HINT_INSTANT, get_instant, get_pydate
from eascheduler.producers.prod_filter_holiday import add_holiday as _add_holiday
from eascheduler.producers.prod_filter_holiday import get_holiday_name as _get_holiday_name
from eascheduler.producers.prod_filter_holiday import get_holidays_by_name as _get_holidays_by_name
from eascheduler.producers.prod_filter_holiday import is_holiday as _is_holiday
from eascheduler.producers.prod_filter_holiday import pop_holiday as _pop_holiday
from eascheduler.producers.prod_sun import get_azimuth_and_elevation


def get_sun_position(instant: HINT_INSTANT) -> tuple[float, float]:
    """Return the sun position (azimuth and elevation) at a given instant.

    :param instant: Instant to get the sun position at or None for now
    :return: Azimuth and elevation of the sun at the specified instant
    """
    return get_azimuth_and_elevation(get_instant(instant))


def is_holiday(date: HINT_DATE) -> bool:
    """Check if a given date is a holiday.

    :param date: Date to check or None for today
    :return: True if the date is a holiday, False otherwise
    """
    return _is_holiday(get_pydate(date))


D = TypeVar('D')


@overload
def pop_holiday(date: HINT_DATE, default: D) -> str | D:
    ...


@overload
def pop_holiday(date: HINT_DATE, default: None = None) -> str | None:
    ...


def pop_holiday(date, default=None):
    """Delete a holiday and return the name of the deleted holiday

    :param date: Date to delete or None for today
    :param default: Default value to return if the date is not a holiday
    :return: Name of the deleted holiday or the default value
    """

    return _pop_holiday(get_pydate(date), default)


@overload
def get_holiday_name(date: HINT_DATE, default: D) -> str | D:
    ...


@overload
def get_holiday_name(date: HINT_DATE, default: None = None) -> str | None:
    ...


def get_holiday_name(date, default=None) -> str:
    """Get the holiday name of a given date if the date is a holiday else return the given default.

    :param date: Date
    :param default: Default value to return if the date is not a holiday
    """

    return _get_holiday_name(get_pydate(date), default)


def get_holidays_by_name(
        name: str, *,
        lookup: Literal['contains', 'exact', 'startswith', 'icontains', 'iexact', 'istartswith'] = 'icontains'
) -> list[dt_date]:
    """Return a list of all holiday dates matching the provided holiday
    name. The match will be made case insensitively and partial matches
    will be included by default

    :param name: The holiday's name to try to match.
    :param lookup:
        The holiday name lookup type:
            contains - case sensitive contains match;
            exact - case sensitive exact match;
            startswith - case sensitive starts with match;
            icontains - case insensitive contains match;
            iexact - case insensitive exact match;
            istartswith - case insensitive starts with match;
    :return:
        A list of all holiday dates matching the provided holiday name.
    """

    return _get_holidays_by_name(name, lookup=lookup)


def add_holiday(date: HINT_DATE, name: str | None = None) -> None:
    """Add a new holiday. If the date is already a holiday the names will be joined together
    with a semicolon as separator.

    :param date: Date for the new holiday.
    :param name: Name of the Holiday, if not provided it will be set to "Holiday"
    """
    return _add_holiday(get_pydate(date), name)
