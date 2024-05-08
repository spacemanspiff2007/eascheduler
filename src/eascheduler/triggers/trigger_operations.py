from __future__ import annotations

from datetime import datetime, time, timedelta
from random import uniform
from typing import TYPE_CHECKING, Callable, Final

from pendulum import instance
from typing_extensions import override

from eascheduler.const import local_tz

from .base import DateTimeOperationBase


if TYPE_CHECKING:
    from pendulum import DateTime


SORT_ORDER: Final = ('func', 'offset', 'jitter', 'earliest', 'latest')


def sort_trigger_operations(x: DateTimeOperationBase):
    return SORT_ORDER.index(x.NAME)


class OffsetDateTimeOperation(DateTimeOperationBase):
    __slots__ = ('offset', )

    NAME: Final = 'offset'

    def __init__(self, offset: timedelta):
        self.offset: Final = offset

    @override
    def apply(self, dt: DateTime) -> DateTime | None:
        return dt + self.offset

    def __eq__(self, other):
        if isinstance(other, OffsetDateTimeOperation):
            return self.offset == other.offset
        return False


class JitterDateTimeOperation(DateTimeOperationBase):
    __slots__ = ('low', 'high')

    NAME: Final = 'jitter'

    def __init__(self, low: float, high: float | None = None):
        if high is None:
            high = low
            low = 0

        if high <= low:
            raise ValueError()

        self.low: Final = low
        self.high: Final = high

    @override
    def apply(self, dt: DateTime) -> DateTime | None:
        return dt + timedelta(seconds=uniform(self.low, self.high))

    def __eq__(self, other):
        if isinstance(other, JitterDateTimeOperation):
            return self.low == other.low and self.high == other.high
        return False


class EarliestDateTimeOperation(DateTimeOperationBase):
    __slots__ = ('earliest', )

    NAME: Final = 'earliest'

    def __init__(self, earliest: time):
        self.earliest: Final = earliest

    @override
    def apply(self, dt: DateTime) -> DateTime | None:
        e = self.earliest
        earliest_dt = dt.set(hour=e.hour, minute=e.minute, second=e.second, microsecond=e.microsecond)
        if dt < earliest_dt:
            return earliest_dt
        return dt

    def __eq__(self, other):
        if isinstance(other, EarliestDateTimeOperation):
            return self.earliest == other.earliest
        return False


class LatestDateTimeOperation(DateTimeOperationBase):
    __slots__ = ('latest', )

    NAME: Final = 'latest'

    def __init__(self, latest: time):
        self.latest: Final = latest

    @override
    def apply(self, dt: DateTime) -> DateTime | None:
        l = self.latest  # noqa: E741
        latest_dt = dt.set(hour=l.hour, minute=l.minute, second=l.second, microsecond=l.microsecond)
        if dt > latest_dt:
            return latest_dt
        return dt

    def __eq__(self, other):
        if isinstance(other, LatestDateTimeOperation):
            return self.latest == other.latest
        return False


class FunctionDateTimeOperation(DateTimeOperationBase):
    __slots__ = ('func', )

    NAME: Final = 'func'

    def __init__(self, func: Callable[[datetime], datetime]):
        self.func: Final = func

    @override
    def apply(self, dt: DateTime) -> DateTime | None:
        if obj := self.func(dt.naive()) is None:
            return None
        return instance(obj, local_tz).astimezone(local_tz)

    def __eq__(self, other):
        if isinstance(other, FunctionDateTimeOperation):
            return self.func is other.func
        return False
