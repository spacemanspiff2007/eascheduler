from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import ProducerFilterBase


if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import time as dt_time

    from pendulum import DateTime


class ProducerFilterGroup(ProducerFilterBase):
    def __init__(self):
        self._filters: tuple[ProducerFilterBase, ...] = ()

    # noinspection PyShadowingBuiltins
    def add_filter(self, filter: ProducerFilterBase):  # noqa: A002
        self._filters = (*self._filters, filter)
        return self

    @override
    def skip(self, dt: DateTime) -> bool:
        return any(f.skip(dt) for f in self._filters)


class InvertingProducerFilterGroup(ProducerFilterGroup):
    @override
    def skip(self, dt: DateTime) -> bool:
        return not any(f.skip(dt) for f in self._filters)


class TimeProducerFilter(ProducerFilterBase):
    __slots__ = ('_lower', '_upper')

    def __init__(self, lower: dt_time | None, upper: dt_time | None):
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
        return dt.isoweekday() not in self._weekdays


class DayOfMonthProducerFilter(ProducerFilterBase):
    __slots__ = ('_days', )

    def __init__(self, days: Iterable[int]):
        super().__init__()
        self._days: Final = frozenset(days)

    @override
    def skip(self, dt: DateTime) -> bool:
        return dt.day not in self._days
