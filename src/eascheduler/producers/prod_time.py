from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import AmbiguousTime, LocalSystemDateTime, SkippedTime, UTCDateTime

from .base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import time as dt_time

    from whenever import Time


class TimeProducer(DateTimeProducerBase):
    __slots__ = ('_time', )

    def __init__(self, time: dt_time | Time) -> None:
        super().__init__()

        self._time: Final = time

    @staticmethod
    def _get_objs(dt: LocalSystemDateTime, time: dt_time | Time) -> Iterable[LocalSystemDateTime]:
        try:
            return [
                LocalSystemDateTime(dt.year, dt.month, dt.day, time.hour, time.minute, time.second, time.microsecond)
            ]
        except SkippedTime:
            return []
        except AmbiguousTime:
            return [
                LocalSystemDateTime(
                    dt.year, dt.month, dt.day, time.hour, time.minute, time.second, time.microsecond,
                    disambiguate='earlier'
                ),
                LocalSystemDateTime(
                    dt.year, dt.month, dt.day, time.hour, time.minute, time.second, time.microsecond,
                    disambiguate='later'
                )
            ]

    @override
    def get_next(self, dt: UTCDateTime) -> UTCDateTime:     # type: ignore[return]
        time = self._time

        next_dt = dt
        for _ in not_infinite_loop():  # noqa: RET503
            for local_dt in self._get_objs(next_dt.as_local(), time):
                next_dt = local_dt.as_utc()
                if next_dt > dt and ((f := self._filter) is None or f.allow(local_dt)):
                    return next_dt

            next_dt = next_dt.add(days=1)
