from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import Instant, RepeatedTime, SkippedTime, SystemDateTime

from .base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from whenever import Time


class TimeProducer(DateTimeProducerBase):
    __slots__ = ('_time', )

    def __init__(self, time: Time) -> None:
        super().__init__()
        self._time: Final = time

    @staticmethod
    def _replace_time(dt: SystemDateTime, time: Time) -> Iterable[SystemDateTime]:
        try:
            return (dt.replace_time(time, disambiguate='raise'),)
        except SkippedTime:
            return ()
        except RepeatedTime:
            return (
                dt.replace_time(time, disambiguate='earlier'),
                dt.replace_time(time, disambiguate='later'),
            )

    @override
    def get_next(self, dt: Instant) -> Instant:     # type: ignore[return]
        time = self._time

        next_dt = dt
        for _ in not_infinite_loop():  # noqa: RET503
            for local_dt in self._replace_time(next_dt.to_system_tz(), time):
                next_dt = local_dt.instant()
                if next_dt > dt and ((f := self._filter) is None or f.allow(local_dt)):
                    return next_dt

            next_dt = next_dt.add(hours=24)
