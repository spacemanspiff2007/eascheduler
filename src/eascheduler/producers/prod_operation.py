from __future__ import annotations

from random import uniform
from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import TimeDelta

from .base import DateTimeProducerBase, DateTimeProducerOperationBase


if TYPE_CHECKING:
    from datetime import time as dt_time

    from whenever import UTCDateTime


class OffsetProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('offset', )

    def __init__(self, producer: DateTimeProducerBase, offset: int) -> None:
        super().__init__(producer)
        self.offset: Final = offset

    @override
    def apply_operation(self, next_dt: UTCDateTime, dt: UTCDateTime) -> UTCDateTime:
        return next_dt.add(seconds=self.offset)


class EarliestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('earliest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: dt_time) -> None:
        super().__init__(producer)
        self.earliest: Final = earliest

    @override
    def apply_operation(self, next_dt: UTCDateTime, dt: UTCDateTime) -> UTCDateTime:
        e = self.earliest
        earliest_dt = next_dt.as_local().replace(
            hour=e.hour, minute=e.minute, second=e.second, microsecond=e.microsecond).as_utc()
        if next_dt < earliest_dt:
            return earliest_dt
        return next_dt


class LatestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('latest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: dt_time) -> None:
        super().__init__(producer)
        self.latest: Final = earliest

    @override
    def apply_operation(self, next_dt: UTCDateTime, dt: UTCDateTime) -> UTCDateTime:
        l = self.latest  # noqa: E741
        latest_dt = next_dt.as_local().replace(
            hour=l.hour, minute=l.minute, second=l.second, microsecond=l.microsecond).as_utc()
        if next_dt < latest_dt:
            return next_dt
        return latest_dt


class JitterProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('low', 'high')

    def __init__(self, producer: DateTimeProducerBase, low: int, high: int | None = None):
        super().__init__(producer)
        if high is None:
            high = low
            low = 0

        if high <= low:
            raise ValueError()

        self.low: Final = low
        self.high: Final = high

    @override
    def apply_operation(self, next_dt: UTCDateTime, dt: UTCDateTime) -> UTCDateTime:
        if (low := self.low) >= 0:
            return next_dt.add(seconds=int(uniform(low, self.high)))

        # We can use the whole interval because we will always
        lowest = (dt - next_dt).in_seconds()
        if lowest < low:
            return next_dt.add(seconds=int(uniform(low, self.high)))

        # shift the interval forward in time
        diff = lowest - low + 0.0001    # Add a small fraction, so we can be sure that we move forward in time
        return next_dt + TimeDelta(seconds=uniform(low + diff, self.high + diff))
