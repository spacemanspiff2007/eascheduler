from __future__ import annotations

from typing import TYPE_CHECKING, Final

from eascheduler.builder.helper import HINT_TIME, get_time
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
    from eascheduler.producers.base import ProducerFilterBase


class FilterObject:
    def __init__(self, filter: ProducerFilterBase) -> None:  # noqa: A002
        self._filter: Final = filter


class FilterBuilder:
    @staticmethod
    def any(*filters: FilterObject) -> FilterObject:
        return FilterObject(AnyGroupProducerFilter([f._filter for f in filters]))

    @staticmethod
    def all(*filters: FilterObject) -> FilterObject:
        return FilterObject(AllGroupProducerFilter([f._filter for f in filters]))

    @staticmethod
    def not_(filter: FilterObject) -> FilterObject:  # noqa: A002
        return FilterObject(InvertingProducerFilter(filter._filter))

    @staticmethod
    def time(lower: HINT_TIME | None = None, upper: HINT_TIME | None = None) -> FilterObject:
        return FilterObject(
            TimeProducerFilter(get_time(lower), get_time(upper))
        )

    @staticmethod
    def weekdays(*weekdays: int) -> FilterObject:
        return FilterObject(DayOfWeekProducerFilter(weekdays))

    @staticmethod
    def days(*days: int) -> FilterObject:
        return FilterObject(DayOfMonthProducerFilter(days))

    @staticmethod
    def months(*months: int) -> FilterObject:
        return FilterObject(MonthOfYearProducerFilter(months))
