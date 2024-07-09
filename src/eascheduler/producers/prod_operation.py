from __future__ import annotations

from random import uniform
from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import LocalDateTime, RepeatedTime, SkippedTime, SystemDateTime, Time, TimeDelta

from .base import DateTimeProducerBase, DateTimeProducerOperationBase


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

    def __init__(self, producer: DateTimeProducerBase, offset: int) -> None:
        super().__init__(producer)
        self.offset: Final = offset

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        return next_dt.add(seconds=self.offset)


class EarliestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('earliest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: Time) -> None:
        super().__init__(producer)
        self.earliest: Final = earliest

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        try:
            earliest_dt = next_dt.to_system_tz().replace_time(self.earliest, disambiguate='raise').instant()
        except SkippedTime:
            earliest_dt = find_time_after_dst_switch(next_dt.to_system_tz(), self.earliest)
        except RepeatedTime:
            earliest_dt = next_dt.to_system_tz().replace_time(self.earliest, disambiguate='earlier').instant()
            if earliest_dt <= dt:
                earliest_dt = next_dt.to_system_tz().replace_time(self.earliest, disambiguate='later').instant()

        if next_dt < earliest_dt:
            return earliest_dt
        return next_dt


class LatestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('latest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: Time) -> None:
        super().__init__(producer)
        self.latest: Final = earliest

    @override
    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        try:
            latest_dt = next_dt.to_system_tz().replace_time(self.latest, disambiguate='raise').instant()
        except SkippedTime:
            latest_dt = find_time_after_dst_switch(next_dt.to_system_tz(), self.latest)
        except RepeatedTime:
            latest_dt = next_dt.to_system_tz().replace_time(self.latest, disambiguate='earlier').instant()
            if latest_dt <= dt:
                latest_dt = next_dt.to_system_tz().replace_time(self.latest, disambiguate='later').instant()

        if next_dt > latest_dt:
            return latest_dt
        return next_dt


class JitterProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('low', 'high')

    def __init__(self, producer: DateTimeProducerBase, low: int, high: int | None = None) -> None:
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
            return next_dt.add(seconds=int(uniform(low, self.high)))

        # We can use the whole interval because we will always
        lowest = (dt - next_dt).in_seconds()
        if lowest < low:
            return next_dt.add(seconds=int(uniform(low, self.high)))

        # shift the interval forward in time
        diff = lowest - low + 0.0001    # Add a small fraction, so we can be sure that we move forward in time
        return next_dt + TimeDelta(seconds=uniform(low + diff, self.high + diff))
