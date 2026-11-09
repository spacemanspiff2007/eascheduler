from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Final, Literal, TypeAlias

from typing_extensions import Self
from whenever import SYSTEM_TZ, Date, PlainDateTime, RepeatedTime, SkippedTime, Time, ZonedDateTime

from eascheduler.helpers.helpers import to_enum


if TYPE_CHECKING:
    from whenever import Time


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


def find_time_after_dst_switch(dt: ZonedDateTime | Date, time: Time) -> ZonedDateTime:
    # DST changes typically occur on the full minute
    t: PlainDateTime = PlainDateTime(dt.year, dt.month, dt.day, time.hour, time.minute)

    # quick path -> try next hour
    candidate_plain: Final = t.add(minutes=60 - time.minute, naive_arithmetic_ok=True)

    try:
        candidate_zoned = candidate_plain.assume_tz(SYSTEM_TZ, disambiguation='raise')

        try:
            candidate_plain.subtract(
                nanoseconds=1, naive_arithmetic_ok=True).assume_tz(SYSTEM_TZ, disambiguation='raise')
        except SkippedTime:
            return candidate_zoned
    except SkippedTime:
        pass

    # dst is typically 1 hour, but who knows
    for _ in range(121):
        t = t.add(minutes=1, naive_arithmetic_ok=True)

        try:
            return ZonedDateTime(dt.year, dt.month, dt.day, t.hour, t.minute, tz=SYSTEM_TZ, disambiguation='raise')
        except SkippedTime:
            continue

    msg = 'Could not find a time after the DST switch'
    raise ValueError(msg)


class TimeSkippedError(Exception):
    pass


class TimeTwiceError(Exception):
    def __init__(self, t1: ZonedDateTime, t2: ZonedDateTime) -> None:
        self.earlier: Final = t1
        self.later: Final = t2


class TimeReplacer:
    __slots__ = ('_repeated', '_skipped', '_time')

    def __init__(self, time: Time, if_skipped: HINT_SKIPPED, if_repeated: HINT_REPEATED) -> None:
        super().__init__()
        self._time: Final = time
        self._skipped: Final[SkippedTimeBehavior] = to_enum(SkippedTimeBehavior, if_skipped)
        self._repeated: Final[RepeatedTimeBehavior] = to_enum(RepeatedTimeBehavior, if_repeated)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeReplacer):
            return NotImplemented
        return self._time == other._time and self._skipped == other._skipped and self._repeated == other._repeated

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} {self._time!s}'
                f' if_skipped={self._skipped.value:s} if_repeated={self._repeated.value:s}>')

    def copy(self) -> Self:
        return self.__class__(self._time, self._skipped, self._repeated)

    def replace(self, dt: ZonedDateTime | Date) -> ZonedDateTime:  # noqa: C901

        kwargs = {
            'year': dt.year, 'month': dt.month, 'day': dt.day,
            'hour': self._time.hour, 'minute': self._time.minute, 'second': self._time.second,
            'nanosecond': self._time.nanosecond
        }

        try:
            return ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='raise')
        except SkippedTime:
            match self._skipped:
                case SkippedTimeBehavior.SKIP:
                    raise TimeSkippedError() from None
                case SkippedTimeBehavior.EARLIER:
                    return ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='earlier')
                case SkippedTimeBehavior.LATER:
                    return ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='later')
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
                    return ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='earlier')
                case RepeatedTimeBehavior.LATER:
                    return ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='later')
                case RepeatedTimeBehavior.TWICE:
                    raise TimeTwiceError(
                        ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='earlier'),
                        ZonedDateTime(**kwargs, tz=SYSTEM_TZ, disambiguation='later'),
                    ) from None
                case _:
                    msg = f'Invalid value: {self._repeated!r}'
                    raise ValueError(msg) from None
