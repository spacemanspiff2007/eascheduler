from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from .base import DateTimeProducerBase


if TYPE_CHECKING:
    from datetime import time as dt_time

    from pendulum import DateTime


class TimeProducer(DateTimeProducerBase):
    __slots__ = ('_time', )

    def __init__(self, time: dt_time) -> None:
        super().__init__()

        self._time: dt_time = time

    @override
    def get_next(self, dt: DateTime) -> DateTime:

        t = self._time
        new_dt = dt.at(t.hour, t.minute, t.second, t.microsecond)

        while new_dt <= dt or ((f := self._filter) is not None and not f.allow(new_dt)):
            new_dt = new_dt.add(days=1)

        return new_dt
