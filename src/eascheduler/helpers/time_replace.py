from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Final

from whenever import LocalDateTime, RepeatedTime, SkippedTime


if TYPE_CHECKING:
    from whenever import SystemDateTime, Time


class SkippedTimeBehavior(str, Enum):
    SKIP = 'skip'
    BEFORE = 'before'
    AFTER = 'after'
    CLOSE = 'close'


class RepeatedTimeBehavior(str, Enum):
    SKIP = 'skip'
    EARLIER = 'earlier'
    LATER = 'later'
    TWICE = 'twice'


def find_time_after_dst_switch(dt: SystemDateTime, time: Time) -> SystemDateTime:
    # DST changes typically occur on the full minute
    local = LocalDateTime(dt.year, dt.month, dt.day, time.hour, time.minute)

    while True:
        local = local.add(minutes=1, ignore_dst=True)

        try:
            return dt.replace_time(local.time(), disambiguate='raise')
        except SkippedTime:
            continue


class TimeReplacer:
    __slots__ = ('_time', '_skipped', '_repeated')

    def __init__(self, time: Time, if_skipped: SkippedTimeBehavior, if_repeated: RepeatedTimeBehavior) -> None:
        super().__init__()
        self._time: Final = time

        if not isinstance(if_skipped, SkippedTimeBehavior):
            if_skipped = SkippedTimeBehavior(if_skipped)
        self._skipped: Final[SkippedTimeBehavior] = if_skipped

        if not isinstance(if_repeated, RepeatedTimeBehavior):
            if_repeated = RepeatedTimeBehavior(if_repeated)
        self._repeated: Final[RepeatedTimeBehavior] = if_repeated

    def replace(self, dt: SystemDateTime) -> SystemDateTime | None:
        try:
            return dt.replace_time(self._time, disambiguate='raise')
        except (SkippedTime, RepeatedTime):
            return None

    def replace_dst(self, dt: SystemDateTime, *, reversed: bool = False) -> tuple[SystemDateTime, ...]:  # noqa: C901, PLR0911
        try:
            return (dt.replace_time(self._time, disambiguate='raise'), )
        except SkippedTime:
            match self._skipped:
                case SkippedTimeBehavior.SKIP:
                    return ()
                case SkippedTimeBehavior.BEFORE:
                    return (dt.replace_time(self._time, disambiguate='earlier'), )
                case SkippedTimeBehavior.AFTER:
                    return (dt.replace_time(self._time, disambiguate='later'), )
                case SkippedTimeBehavior.CLOSE:
                    return (find_time_after_dst_switch(dt, self._time), )
                case _:
                    msg = f'Invalid value: {self._skipped!r}'
                    raise ValueError(msg) from None
        except RepeatedTime:
            match self._repeated:
                case RepeatedTimeBehavior.SKIP:
                    return ()
                case RepeatedTimeBehavior.EARLIER:
                    return (dt.replace_time(self._time, disambiguate='earlier'), )
                case RepeatedTimeBehavior.LATER:
                    return (dt.replace_time(self._time, disambiguate='later'), )
                case RepeatedTimeBehavior.TWICE:
                    return (
                        dt.replace_time(self._time, disambiguate='earlier' if not reversed else 'later'),
                        dt.replace_time(self._time, disambiguate='later' if not reversed else 'earlier')
                    )
                case _:
                    msg = f'Invalid value: {self._repeated!r}'
                    raise ValueError(msg) from None
