from __future__ import annotations

from random import uniform
from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import LocalDateTime, SkippedTime, SystemDateTime, Time, TimeDelta

from eascheduler.helpers import TimeReplacer, TimeSkippedError, TimeTwiceError
from eascheduler.producers.base import DateTimeProducerBase, DateTimeProducerOperationBase


if TYPE_CHECKING:
    from whenever import Instant


def find_time_after_dst_switch(dt: SystemDateTime, time: Time) -> Instant:
    # DST changes typically occur on the full minute
    local = LocalDateTime(dt.year, dt.month, dt.day, time.hour, time.minute)

    while True:
        local = local.add(minutes=1, ignore_dst=True)

        try:
            return dt.replace_time(local.time(), disambiguate='raise').instant()
        except SkippedTime:
            continue


class OffsetProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('offset', )

    def __init__(self, producer: DateTimeProducerBase, offset: float) -> None:
        super().__init__(producer)
        self.offset: Final = offset

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        return next_dt.add(seconds=self.offset)


class EarliestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('earliest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: TimeReplacer) -> None:
        super().__init__(producer)
        self.earliest: Final = earliest

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        try:
            earliest_dt = self.earliest.replace(next_dt.to_system_tz()).instant()
        except TimeSkippedError:
            return next_dt
        except TimeTwiceError as e:
            earliest_dt = e.earlier.instant()
            if earliest_dt <= dt:
                earliest_dt = e.later.instant()

        if next_dt < earliest_dt:
            return earliest_dt
        return next_dt


class LatestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('latest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: TimeReplacer) -> None:
        super().__init__(producer)
        self.latest: Final = earliest

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        try:
            latest_dt = self.latest.replace(next_dt.to_system_tz()).instant()
        except TimeSkippedError:
            return next_dt
        except TimeTwiceError as e:
            latest_dt = e.earlier.instant()
            if latest_dt <= dt:
                latest_dt = e.later.instant()

        if next_dt > latest_dt:
            return latest_dt
        return next_dt


class JitterProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('low', 'high')

    def __init__(self, producer: DateTimeProducerBase, low: float, high: float | None = None) -> None:
        super().__init__(producer)
        if high is None:
            high = low
            low = 0

        if high <= low:
            raise ValueError()

        self.low: Final = low
        self.high: Final = high

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        if (low := self.low) >= 0:
            return next_dt.add(seconds=uniform(low, self.high))

        # Check if we can use the whole interval
        lowest = (dt - next_dt).in_seconds()
        if lowest < low:
            return next_dt.add(seconds=uniform(low, self.high))

        # shift the interval forward in time
        diff = lowest - low + 0.0001    # Add a small fraction, so we can be sure that we move forward in time
        return next_dt + TimeDelta(seconds=uniform(low + diff, self.high + diff))
