from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self, override

from eascheduler.producers.base import ProducerFilterBase


if TYPE_CHECKING:
    from collections.abc import Iterable

    from whenever import SystemDateTime, Time


class ProducerFilterGroupBase(ProducerFilterBase):
    __slots__ = ('_filters', )

    def __init__(self, filters: Iterable[ProducerFilterBase] | None = None) -> None:
        self._filters: tuple[ProducerFilterBase, ...] = () if filters is None else tuple(filters)

    # noinspection PyShadowingBuiltins
    def add_filter(self, filter: ProducerFilterBase) -> Self:  # noqa: A002
        self._filters = (*self._filters, filter)
        return self


class AnyGroupProducerFilter(ProducerFilterGroupBase):
    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return any(f.allow(dt) for f in self._filters)


class AllGroupProducerFilter(ProducerFilterGroupBase):
    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return all(f.allow(dt) for f in self._filters)


class InvertingProducerFilter(ProducerFilterBase):
    __slots__ = ('_filter', )

    # noinspection PyShadowingBuiltins
    def __init__(self, filter: ProducerFilterBase) -> None:  # noqa: A002
        self._filter: ProducerFilterBase = filter

    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return not self._filter.allow(dt)


class TimeProducerFilter(ProducerFilterBase):
    __slots__ = ('_lower', '_upper')

    def __init__(self, lower: Time | None = None, upper: Time | None = None) -> None:
        super().__init__()
        self._lower: Final = lower
        self._upper: Final = upper

    @override
    def allow(self, dt: SystemDateTime) -> bool:

        time = dt.time()
        if (lower := self._lower) is not None and time < lower:
            return False

        if (upper := self._upper) is not None and time >= upper:  # noqa: SIM103
            return False

        return True


class DayOfWeekProducerFilter(ProducerFilterBase):
    __slots__ = ('_weekdays', )

    def __init__(self, weekdays: Iterable[int]) -> None:
        super().__init__()
        self._weekdays: Final = frozenset(weekdays)

    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return dt.py_datetime().isoweekday() in self._weekdays


class DayOfMonthProducerFilter(ProducerFilterBase):
    __slots__ = ('_days', )

    def __init__(self, days: Iterable[int]) -> None:
        super().__init__()
        self._days: Final = frozenset(days)

    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return dt.day in self._days


class MonthOfYearProducerFilter(ProducerFilterBase):
    __slots__ = ('_months', )

    def __init__(self, months: Iterable[int]) -> None:
        super().__init__()
        self._months: Final = frozenset(months)

    @override
    def allow(self, dt: SystemDateTime) -> bool:
        return dt.month in self._months
