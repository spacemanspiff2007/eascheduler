from __future__ import annotations

import re
from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import TypeAlias

from whenever import Instant, SystemDateTime, TimeDelta


T_HINT: TypeAlias = dt_datetime | dt_time | dt_timedelta | TimeDelta | str | None

RE_TIME = re.compile(r'(?P<hour>[0-5]?\d)\s*:\s*(?P<minute>[0-5]?\d)(?:\s*:\s*(?P<second>[0-5]?\d))?')


def get_utc(value: T_HINT) -> Instant:
    if value is None:
        return Instant.now()

    if isinstance(value, dt_datetime):
        return SystemDateTime.from_py_datetime(value).to_utc()

    # ------------------------------------------------------------------------------------------------------------------
    # timedelta
    if isinstance(value, dt_timedelta):
        return Instant.now() + TimeDelta.from_py_timedelta(value)

    if isinstance(value, TimeDelta):
        return Instant.now() + value

    # ------------------------------------------------------------------------------------------------------------------
    # time
    if isinstance(value, dt_time):
        now = SystemDateTime.now()
        new = now.replace(
            hour=value.hour, minute=value.minute, second=value.second, microsecond=value.microsecond).to_utc()
        if new < now:
            new = new.add(days=1)
        return new

    if isinstance(value, str):
        if m := RE_TIME.fullmatch(value):
            return SystemDateTime.now().replace(
                hour=int(m['hour']), minute=int(m['minute']), second=int(m['second'] or 0)).as_utc()

    raise ValueError()
