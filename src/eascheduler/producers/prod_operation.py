from __future__ import annotations

from random import uniform
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import DateTimeProducerBase, DateTimeProducerOperationBase, not_infinite_loop


if TYPE_CHECKING:
    from datetime import time as dt_time

    from pendulum import DateTime


class OffsetProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('offset', )

    def __init__(self, producer: DateTimeProducerBase, offset: float) -> None:
        super().__init__(producer)
        self.offset: Final = offset

    @override
    def get_next(self, dt: DateTime) -> DateTime:   # type: ignore[return]
        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503
            next_dt = self._producer.get_next(next_dt)
            offset_dt = next_dt.add(seconds=self.offset)
            if offset_dt > dt:
                return offset_dt


class EarliestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('earliest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: dt_time) -> None:
        super().__init__(producer)
        self.earliest: Final = earliest

    @override
    def get_next(self, dt: DateTime) -> DateTime:
        next_dt = self._producer.get_next(dt)

        e = self.earliest
        earliest_dt = next_dt.set(hour=e.hour, minute=e.minute, second=e.second, microsecond=e.microsecond)
        if next_dt < earliest_dt:
            return earliest_dt
        return next_dt


class LatestProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('latest',)

    def __init__(self, producer: DateTimeProducerBase, earliest: dt_time) -> None:
        super().__init__(producer)
        self.latest: Final = earliest

    @override
    def get_next(self, dt: DateTime) -> DateTime:   # type: ignore[return]
        l = self.latest  # noqa: E741
        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503
            next_dt = self._producer.get_next(next_dt)

            latest_dt = next_dt.set(hour=l.hour, minute=l.minute, second=l.second, microsecond=l.microsecond)
            if latest_dt >= next_dt:
                return next_dt

            if latest_dt > dt:
                return latest_dt


class JitterProducerOperation(DateTimeProducerOperationBase):
    __slots__ = ('low', 'high')

    def __init__(self, producer: DateTimeProducerBase, low: float, high: float | None = None):
        super().__init__(producer)
        if high is None:
            high = low
            low = 0

        if high <= low:
            raise ValueError()

        self.low: Final = low
        self.high: Final = high

    @override
    def get_next(self, dt: DateTime) -> DateTime:
        next_dt = self._producer.get_next(dt)

        if (low := self.low) >= 0:
            return next_dt.add(seconds=uniform(low, self.high))

        lowest = (dt - next_dt).total_seconds()
        if lowest < low:
            return next_dt.add(seconds=uniform(low, self.high))

        # shift the interval forward in time
        diff = lowest - low
        return next_dt.add(seconds=uniform(low + diff, self.high + diff))
