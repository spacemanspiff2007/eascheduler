from __future__ import annotations

from typing import TYPE_CHECKING, Final

from eascheduler.producers import (
    AllGroupProducerFilter,
    AnyGroupProducerFilter,
    DayOfMonthProducerFilter,
    DayOfWeekProducerFilter,
    InvertingProducerFilter,
    MonthOfYearProducerFilter,
    TimeProducerFilter,
)


if TYPE_CHECKING:
    from datetime import time as dt_time

    from eascheduler.producers.base import ProducerFilterBase


class FilterObject:
    def __init__(self, filter: ProducerFilterBase):  # noqa: A002
        self._filter: Final = filter


class FilterBuilder:
    @staticmethod
    def any(*filters: FilterObject) -> FilterObject:
        return FilterObject(AnyGroupProducerFilter([f._filter for f in filters]))

    @staticmethod
    def all(*filters: FilterObject) -> FilterObject:
        return FilterObject(AllGroupProducerFilter([f._filter for f in filters]))

    @staticmethod
    def not_(filter: FilterObject):  # noqa: A002
        return FilterObject(InvertingProducerFilter(filter._filter))

    @staticmethod
    def time(lower: dt_time | None = None, upper: dt_time | None = None):
        return FilterObject(TimeProducerFilter(lower, upper))

    @staticmethod
    def weekdays(*weekdays: int) -> FilterObject:
        return FilterObject(DayOfWeekProducerFilter(weekdays))

    @staticmethod
    def days(*days: int) -> FilterObject:
        return FilterObject(DayOfMonthProducerFilter(days))

    @staticmethod
    def months(*months: int) -> FilterObject:
        return FilterObject(MonthOfYearProducerFilter(months))
