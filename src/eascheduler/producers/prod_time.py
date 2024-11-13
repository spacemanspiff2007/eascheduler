from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from eascheduler.helpers import TimeReplacer, TimeSkippedError, TimeTwiceError
from eascheduler.producers.base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from whenever import Instant


class TimeProducer(DateTimeProducerBase):
    __slots__ = ('_time', )

    def __init__(self, time: TimeReplacer) -> None:
        super().__init__()
        self._time: Final = time

    @override
    def get_next(self, dt: Instant) -> Instant:     # type: ignore[return]

        date = dt.to_system_tz().date()
        for _ in not_infinite_loop():  # noqa: RET503
            try:
                local_dts = (self._time.replace(date), )
            except TimeSkippedError:
                local_dts = ()
            except TimeTwiceError as e:
                local_dts = (e.earlier, e.later)

            for local_dt in local_dts:
                next_dt = local_dt.instant()
                if next_dt > dt and ((f := self._filter) is None or f.allow(local_dt)):
                    return next_dt

            date = date.add(days=1)
