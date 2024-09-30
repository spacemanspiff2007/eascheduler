from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Final, Literal, TypeAlias

from whenever import LocalDateTime, RepeatedTime, SkippedTime

from eascheduler.helpers.helpers import to_enum


if TYPE_CHECKING:
    from whenever import SystemDateTime, Time


class SkippedTimeBehavior(str, Enum):
    SKIP = 'skip'           # skip job execution entirely
    EARLIER = 'earlier'     # execute job one hour earlier preserving minutes and seconds
    LATER = 'later'         # execute job one hour later preserving minutes and seconds
    AFTER = 'after'         # execute the job directly after the dst change


HINT_SKIPPED: TypeAlias = SkippedTimeBehavior | Literal['skip', 'earlier', 'later', 'after']


class RepeatedTimeBehavior(str, Enum):
    SKIP = 'skip'
    EARLIER = 'earlier'
    LATER = 'later'
    TWICE = 'twice'


HINT_REPEATED: TypeAlias = RepeatedTimeBehavior | Literal['skip', 'earlier', 'later', 'twice']


def find_time_after_dst_switch(dt: SystemDateTime, time: Time) -> SystemDateTime:
    # DST changes typically occur on the full minute
    local = LocalDateTime(dt.year, dt.month, dt.day, time.hour, time.minute)

    while True:
        local = local.add(minutes=1, ignore_dst=True)

        try:
            return dt.replace_time(local.time(), disambiguate='raise')
        except SkippedTime:
            continue


class TimeSkippedError(Exception):
    pass


class TimeTwiceError(Exception):
    def __init__(self, t1: SystemDateTime, t2: SystemDateTime) -> None:
        self.earlier: Final = t1
        self.later: Final = t2


class TimeReplacer:
    __slots__ = ('_time', '_skipped', '_repeated')

    def __init__(self, time: Time, if_skipped: HINT_SKIPPED, if_repeated: HINT_REPEATED) -> None:
        super().__init__()
        self._time: Final = time
        self._skipped: Final[SkippedTimeBehavior] = to_enum(SkippedTimeBehavior, if_skipped)
        self._repeated: Final[RepeatedTimeBehavior] = to_enum(RepeatedTimeBehavior, if_repeated)

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} {self._time!s}'
                f' if_skipped={self._skipped.value:s} if_repeated={self._repeated.value:s}>')

    def replace(self, dt: SystemDateTime) -> SystemDateTime:  # noqa: C901
        try:
            return dt.replace_time(self._time, disambiguate='raise')
        except SkippedTime:
            match self._skipped:
                case SkippedTimeBehavior.SKIP:
                    raise TimeSkippedError() from None
                case SkippedTimeBehavior.EARLIER:
                    return dt.replace_time(self._time, disambiguate='earlier')
                case SkippedTimeBehavior.LATER:
                    return dt.replace_time(self._time, disambiguate='later')
                case SkippedTimeBehavior.AFTER:
                    return find_time_after_dst_switch(dt, self._time)
                case _:
                    msg = f'Invalid value: {self._skipped!r}'
                    raise ValueError(msg) from None
        except RepeatedTime:
            match self._repeated:
                case RepeatedTimeBehavior.SKIP:
                    raise TimeSkippedError() from None
                case RepeatedTimeBehavior.EARLIER:
                    return dt.replace_time(self._time, disambiguate='earlier')
                case RepeatedTimeBehavior.LATER:
                    return dt.replace_time(self._time, disambiguate='later')
                case RepeatedTimeBehavior.TWICE:
                    raise TimeTwiceError(
                        dt.replace_time(self._time, disambiguate='earlier'),
                        dt.replace_time(self._time, disambiguate='later'),
                    ) from None
                case _:
                    msg = f'Invalid value: {self._repeated!r}'
                    raise ValueError(msg) from None
