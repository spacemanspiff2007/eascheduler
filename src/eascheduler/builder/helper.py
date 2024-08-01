from __future__ import annotations

from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import TypeAlias

from whenever import Instant, SystemDateTime, Time, TimeDelta

from eascheduler.helpers import HINT_CLOCK_BACKWARD, HINT_CLOCK_FORWARD, TimeReplacer, check_dst_handling


HINT_TIME: TypeAlias = dt_time | Time | str
HINT_TIMEDELTA: TypeAlias = dt_timedelta | TimeDelta | int | float | str
HINT_INSTANT: TypeAlias = dt_datetime | None | str | HINT_TIME, HINT_TIMEDELTA


def get_timedelta(value: HINT_TIMEDELTA) -> TimeDelta:
    match value:
        case dt_timedelta():
            return TimeDelta.from_py_timedelta(value)
        case TimeDelta():
            return value
        case int() | float():
            return TimeDelta(seconds=value)
        case str():
            return TimeDelta.parse_common_iso(value)
        case _:
            raise TypeError()


def get_pos_timedelta_secs(value: HINT_TIMEDELTA) -> float:
    if (value := get_timedelta(value).in_seconds()) <= 0:
        msg = 'Value must be positive.'
        raise ValueError(msg)
    return value


def get_time(value: HINT_TIME) -> Time:
    match value:
        case Time():
            return value
        case dt_time():
            return Time.from_py_time(value)
        case str():
            return Time.parse_common_iso(value)
        case _:
            raise TypeError()


def get_time_replacer(value: HINT_TIME, *,
                      clock_forward: HINT_CLOCK_FORWARD, clock_backward: HINT_CLOCK_BACKWARD) -> TimeReplacer:
    time = get_time(value)
    f, b = check_dst_handling(time, clock_forward, clock_backward)
    return TimeReplacer(time, f, b)


def get_instant(value: HINT_INSTANT) -> Instant:

    match value:
        case None:
            return Instant.now()
        case dt_datetime():
            return SystemDateTime.from_py_datetime(value).instant()
        case SystemDateTime():
            return value.instant()

    # ------------------------------------------------------------------------------------------------------------------
    # timedelta
    try:
        timedelta = get_timedelta(value)
    except ValueError:
        pass
    else:
        return Instant.now() + timedelta

    # ------------------------------------------------------------------------------------------------------------------
    # time
    try:
        time = get_time(value)
    except ValueError:
        pass
    else:
        now = SystemDateTime.now()
        new = now.replace_time(time, disambiguate='raise')
        if new < now:
            new = new.add(days=1)
        return new.instant()

    raise ValueError()
