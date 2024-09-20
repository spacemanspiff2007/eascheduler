from __future__ import annotations

from typing import Final

from holidays import HolidayBase as _HolidayBase

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
    TimeProducerFilter,
)
from eascheduler.producers.base import ProducerFilterBase


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
        """Let only certain weekdays pass through"""
        return FilterObject(DayOfWeekProducerFilter(get_weekdays(weekdays)))

    @staticmethod
    def days(*days: HINT_NAME_OR_NR) -> FilterObject:
        """Let only certain days pass through"""
        return FilterObject(DayOfMonthProducerFilter(get_days(days)))

    @staticmethod
    def months(*months: HINT_NAME_OR_NR) -> FilterObject:
        """Let only certain months pass through"""
        return FilterObject(MonthOfYearProducerFilter(get_months(months)))

    @staticmethod
    def holidays(holidays: _HolidayBase | None = None) -> FilterObject:
        """Let only holidays pass through

        :param holidays:
            Optional holiday object to use. If not provided the default holiday object will be used
            Userful if you want to use holidays from e.g. another country or another subdivision
        """

        return FilterObject(HolidayProducerFilter(holidays))
