from __future__ import annotations

import re
from datetime import datetime as dt_datetime
from datetime import time as dt_time
from typing import TypeAlias

from whenever import LocalSystemDateTime, TimeDelta, UTCDateTime


T_HINT: TypeAlias = dt_datetime | dt_time | str | None

RE_TIME = re.compile(r'(?P<hour>[0-5]?\d)\s*:\s*(?P<minute>[0-5]?\d)(?:\s*:\s*(?P<second>[0-5]?\d))?')


def get_utc(value: T_HINT) -> UTCDateTime:
    if value is None:
        return UTCDateTime.now()

    if isinstance(value, dt_datetime):
        return LocalSystemDateTime.from_py_datetime(value).as_utc()

    if isinstance(value, dt_time):
        now = LocalSystemDateTime.now()
        new = now.replace(
            hour=value.hour, minute=value.minute, second=value.second, microsecond=value.microsecond).as_utc()
        if new < now:
            new = new.add(days=1)
        return new

    if isinstance(value, str):
        if m := RE_TIME.fullmatch(value):
            return LocalSystemDateTime.now().replace(
                hour=int(m['hour']), minute=int(m['minute']), second=int(m['second'] or 0)).as_utc()

    raise ValueError()
