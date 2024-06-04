from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import ProducerFilterBase


if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import time as dt_time

    from pendulum import DateTime


class ProducerFilterGroupBase(ProducerFilterBase):
    __slots__ = ('_filters', )

    def __init__(self, filters: Iterable[ProducerFilterBase] | None = None):
        self._filters: tuple[ProducerFilterBase, ...] = () if filters is None else tuple(filters)

    # noinspection PyShadowingBuiltins
    def add_filter(self, filter: ProducerFilterBase):  # noqa: A002
        self._filters = (*self._filters, filter)
        return self


class AnyGroupProducerFilter(ProducerFilterGroupBase):
    @override
    def skip(self, dt: DateTime) -> bool:
        return any(f.skip(dt) for f in self._filters)


class AllGroupProducerFilter(ProducerFilterGroupBase):
    @override
    def skip(self, dt: DateTime) -> bool:
        return all(f.skip(dt) for f in self._filters)


class InvertingProducerFilter(ProducerFilterBase):
    __slots__ = ('_filter', )

    # noinspection PyShadowingBuiltins
    def __init__(self, filter: ProducerFilterBase):  # noqa: A002
        self._filter: ProducerFilterBase = filter

    @override
    def skip(self, dt: DateTime) -> bool:
        return not self._filter.skip(dt)


class TimeProducerFilter(ProducerFilterBase):
    __slots__ = ('_lower', '_upper')

    def __init__(self, lower: dt_time | None = None, upper: dt_time | None = None):
        super().__init__()
        self._lower = lower
        self._upper = upper

    @override
    def skip(self, dt: DateTime) -> bool:

        time = dt.time()
        if (lower := self._lower) is not None and time < lower:
            return True

        if (upper := self._upper) is not None and time > upper:
            return True

        return False


class DayOfWeekProducerFilter(ProducerFilterBase):
    __slots__ = ('_weekdays', )

    def __init__(self, weekdays: Iterable[int]):
        super().__init__()
        self._weekdays: Final = frozenset(weekdays)

    @override
    def skip(self, dt: DateTime) -> bool:
        return dt.isoweekday() in self._weekdays


class DayOfMonthProducerFilter(ProducerFilterBase):
    __slots__ = ('_days', )

    def __init__(self, days: Iterable[int]):
        super().__init__()
        self._days: Final = frozenset(days)

    @override
    def skip(self, dt: DateTime) -> bool:
        return dt.day in self._days


class MonthOfYearProducerFilter(ProducerFilterBase):
    __slots__ = ('_months', )

    def __init__(self, months: Iterable[int]):
        super().__init__()
        self._months: Final = frozenset(months)

    @override
    def skip(self, dt: DateTime) -> bool:
        return dt.month in self._months