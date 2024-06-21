from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import DateTimeProducerBase


if TYPE_CHECKING:
    from pendulum import DateTime


class IntervalProducer(DateTimeProducerBase):
    __slots__ = ('_interval', '_next', )

    def __init__(self, start: DateTime, interval: int) -> None:
        super().__init__()

        self._interval: Final = interval
        self._next: DateTime = start

    @override
    def get_next(self, dt: DateTime) -> DateTime:
        interval = self._interval
        new_dt = self._next

        # The producer should be stateless. We still need the DateTime in case we have odd intervals.
        # That's why we move backwards in time here
        while new_dt > dt:
            new_dt = new_dt.subtract(seconds=interval)

        while new_dt <= dt or ((f := self._filter) is not None and not f.allow(new_dt)):
            new_dt = new_dt.add(seconds=interval)

        self._next = new_dt
        return new_dt
