from __future__ import annotations

from typing import TYPE_CHECKING, Final

from eascheduler.builder.helper import (
    HINT_NAME_OR_NR,
    HINT_TIME,
    BuilderTypeValidator,
    get_days,
    get_months,
    get_time,
    get_weekdays,
)
from eascheduler.producers import (
    AllGroupProducerFilter,
    AnyGroupProducerFilter,
    DayOfMonthProducerFilter,
    DayOfWeekProducerFilter,
    HolidayProducerFilter,
    InvertingProducerFilter,
    MonthOfYearProducerFilter,
    NotWorkDayProducerFilter,
    TimeProducerFilter,
    WorkDayProducerFilter,
)
from eascheduler.producers.base import ProducerFilterBase


if TYPE_CHECKING:
    from holidays import HolidayBase as _HolidayBase


class FilterObject:
    def __init__(self, filter: ProducerFilterBase) -> None:  # noqa: A002
        self._filter: Final = filter


_get_producer_filter = BuilderTypeValidator(FilterObject, ProducerFilterBase, '_filter')


# noinspection PyProtectedMember,PyShadowingBuiltins
class FilterBuilder:
    @staticmethod
    def any(*filters: FilterObject) -> FilterObject:
        """Passes an instant as soon as any of the filters passes it"""
        return FilterObject(AnyGroupProducerFilter([_get_producer_filter(f) for f in filters]))

    @staticmethod
    def all(*filters: FilterObject) -> FilterObject:
        """Passes an instant only when all the filters pass it"""
        return FilterObject(AllGroupProducerFilter([_get_producer_filter(f) for f in filters]))

    @staticmethod
    def not_(filter: FilterObject) -> FilterObject:  # noqa: A002
        """Invert a filter"""
        return FilterObject(InvertingProducerFilter(_get_producer_filter(filter)))

    @staticmethod
    def time(lower: HINT_TIME | None = None, upper: HINT_TIME | None = None) -> FilterObject:
        """Restrict the trigger instant to a time range"""
        return FilterObject(
            TimeProducerFilter(get_time(lower), get_time(upper))
        )

    @staticmethod
    def weekdays(*weekdays: HINT_NAME_OR_NR) -> FilterObject:
        """Let only certain weekdays pass through

        :param weekdays: days of week as str, int, or str range (``'Mon-Fri'``, ``'Sun-Mon'``, ``'Mo-Mi``, ``'Fr-So'``)
        """
        return FilterObject(DayOfWeekProducerFilter(get_weekdays(weekdays)))

    @staticmethod
    def days(*days: HINT_NAME_OR_NR) -> FilterObject:
        """Let only certain days of the month pass through

        :param days: days of the month as str, int, or str range (``'1-7'``, ``'1-5,10-15'``, ``'1,5,7'``)
        """
        return FilterObject(DayOfMonthProducerFilter(get_days(days)))

    @staticmethod
    def months(*months: HINT_NAME_OR_NR) -> FilterObject:
        """Let only certain months pass through

        :param months: Month as str, int, or str range (``'Jan-Jun'``, ``'1-3,10-12'``, ``'Oct-Feb'``, ``'Jan, March'``)
        """
        return FilterObject(MonthOfYearProducerFilter(get_months(months)))

    @staticmethod
    def holidays(holidays: _HolidayBase | None = None) -> FilterObject:
        """Let only holidays pass through

        :param holidays:
            Optional holiday object to use. If not provided the default holiday object will be used
            Userful if you want to use holidays from e.g. another country or another subdivision
        """

        return FilterObject(HolidayProducerFilter(holidays))

    @staticmethod
    def work_days(holidays: _HolidayBase | None = None) -> FilterObject:
        """Let only working days pass through

        :param holidays:
            Optional holiday object to use. If not provided the default holiday object will be used
            Userful if you want to use holidays from e.g. another country or another subdivision
        """

        return FilterObject(WorkDayProducerFilter(holidays))

    @staticmethod
    def not_work_days(holidays: _HolidayBase | None = None) -> FilterObject:
        """Let only days pass through that are not working days

        :param holidays:
            Optional holiday object to use. If not provided the default holiday object will be used
            Userful if you want to use holidays from e.g. another country or another subdivision
        """

        return FilterObject(NotWorkDayProducerFilter(holidays))
