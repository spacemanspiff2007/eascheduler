from __future__ import annotations

from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import TypeAlias

from whenever import Instant, SystemDateTime, Time, TimeDelta

from eascheduler.helpers import HINT_CLOCK_BACKWARD, HINT_CLOCK_FORWARD, TimeReplacer, check_dst_handling


HINT_TIME: TypeAlias = dt_time | Time | str
HINT_INSTANT: TypeAlias = dt_datetime | dt_timedelta | TimeDelta | str | None | HINT_TIME


def get_time(value: HINT_TIME) -> Time:
    if isinstance(value, dt_time):
        return Time.from_py_time(value)

    if isinstance(value, Time):
        return value

    if isinstance(value, str):
        try:
            return Time.parse_common_iso(value)
        except ValueError:
            pass

    raise ValueError()


def get_time_replacer(value: HINT_TIME, *,
                      clock_forward: HINT_CLOCK_FORWARD, clock_backward: HINT_CLOCK_BACKWARD) -> TimeReplacer:
    time = get_time(value)
    f, b = check_dst_handling(time, clock_forward, clock_backward)
    return TimeReplacer(time, f, b)


def get_instant(value: HINT_INSTANT) -> Instant:  # noqa: C901
    if value is None:
        return Instant.now()

    # ------------------------------------------------------------------------------------------------------------------
    # datetime
    if isinstance(value, dt_datetime):
        return SystemDateTime.from_py_datetime(value).instant()

    # ------------------------------------------------------------------------------------------------------------------
    # timedelta
    if isinstance(value, dt_timedelta):
        return Instant.now() + TimeDelta.from_py_timedelta(value)

    if isinstance(value, TimeDelta):
        return Instant.now() + value

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

    # ------------------------------------------------------------------------------------------------------------------
    # str
    if isinstance(value, str):
        for parser in (SystemDateTime.parse_common_iso, TimeDelta.parse_common_iso):
            try:
                obj = parser(value)
            except ValueError:
                continue
            return get_instant(obj)

    raise ValueError()
