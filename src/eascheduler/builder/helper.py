from __future__ import annotations

from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import TypeAlias

from whenever import Instant, SystemDateTime, Time, TimeDelta


T_HINT: TypeAlias = dt_datetime | dt_time | dt_timedelta | TimeDelta | str | None


def get_time(value: dt_time | Time | str) -> Time:
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


def get_utc(value: T_HINT) -> Instant:  # noqa: C901
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
        new = now.replace_time(time)
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
            return get_utc(obj)

    raise ValueError()
