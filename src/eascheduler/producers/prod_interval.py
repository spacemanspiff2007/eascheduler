from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import DateTimeProducerBase


if TYPE_CHECKING:
    from whenever import Instant


class IntervalProducer(DateTimeProducerBase):
    __slots__ = ('_interval', '_next', )

    def __init__(self, start: Instant | None, interval: float) -> None:
        super().__init__()

        self._next: Instant | None = start
        self._interval: Final = interval

    @override
    def get_next(self, dt: Instant) -> Instant:
        interval = self._interval

        # Possibility to immediately start the interval
        if (new_dt := self._next) is None:
            new_dt = dt.add(microseconds=1)

        # The producer should be stateless. We still need the DateTime in case we have odd intervals.
        # That's why we move backwards in time here
        while new_dt > dt:
            new_dt = new_dt.subtract(seconds=interval)

        while new_dt <= dt or ((f := self._filter) is not None and not f.allow(new_dt.to_system_tz())):
            new_dt = new_dt.add(seconds=interval)

        self._next = new_dt
        return new_dt
