from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from holidays import HolidayBase as _HolidayBase
from holidays import country_holidays
from typing_extensions import override

from eascheduler.errors.errors import HolidaysNotSetUpError
from eascheduler.producers.base import ProducerFilterBase


if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date as dt_date

    from whenever import SystemDateTime


class HolidayProducerFilterBase(ProducerFilterBase):
    __slots__ = ('_holidays', )

    def __init__(self, holidays: _HolidayBase | None = None) -> None:
        super().__init__()
        self._holidays: Final = _get_holiday_obj(holidays)


class HolidayProducerFilter(HolidayProducerFilterBase):
    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return dt.date().py_date() in self._holidays


class NotWorkDayProducerFilter(HolidayProducerFilterBase):
    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return not self._holidays.is_working_day(dt.date().py_date())


class WorkDayProducerFilter(HolidayProducerFilterBase):

    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return self._holidays.is_working_day(dt.date().py_date())


def _get_holiday_obj(holidays: _HolidayBase | None = None) -> _HolidayBase:
    if holidays is None:
        if HOLIDAYS is None:
            raise HolidaysNotSetUpError()
        return HOLIDAYS

    if isinstance(holidays, _HolidayBase):
        return holidays

    raise TypeError()


HOLIDAYS: _HolidayBase | None = None


def setup_holidays(country: str, subdiv: str | None = None, *, observed: bool = True, language: str | None = None,
                   categories: str | Iterable[str] | None = None) -> None:
    """Set up the holidays

    :param country:
        An ISO 3166-1 Alpha-2 country code.

    :param subdiv:
        The subdivision (e.g. state or province) as a ISO 3166-2 code
        or its alias; not implemented for all countries (see documentation).

    :param observed:
        Whether to include the dates of when public holiday are observed
        (e.g. a holiday falling on a Sunday being observed the following
        Monday). False may not work for all countries.

    :param language:
        The language which the returned holiday names will be translated
        into. It must be an ISO 639-1 (2-letter) language code. If the
        language translation is not supported the original holiday names
        will be used.

    :param categories:
        Requested holiday categories.

    :return:
    """
    global HOLIDAYS

    if HOLIDAYS is not None:
        msg = 'Holidays are already set!'
        raise ValueError(msg)

    HOLIDAYS = country_holidays(country, subdiv, observed=observed, language=language, categories=categories)


def is_holiday(dt: dt_date) -> bool:
    if HOLIDAYS is None:
        raise HolidaysNotSetUpError()

    return dt in HOLIDAYS


def pop_holiday(dt: dt_date, default: Any = None) -> None | str:
    if HOLIDAYS is None:
        raise HolidaysNotSetUpError()

    try:
        return HOLIDAYS.pop(dt)
    except KeyError:
        return default


def get_holiday_name(dt: dt_date, default: Any = None) -> None | str:
    if HOLIDAYS is None:
        raise HolidaysNotSetUpError()
    return HOLIDAYS.get(dt, default)


def get_holidays_by_name(name: str, lookup: str) -> list[dt_date]:
    if HOLIDAYS is None:
        raise HolidaysNotSetUpError()

    return HOLIDAYS.get_named(name, lookup)


def add_holiday(dt: dt_date, name: str | None = None) -> None:
    if HOLIDAYS is None:
        raise HolidaysNotSetUpError()

    if name is not None:
        HOLIDAYS.update({dt: name})
    else:
        HOLIDAYS.append(dt)
