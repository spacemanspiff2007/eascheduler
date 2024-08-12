from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import TypeAlias

from whenever import Instant, SystemDateTime, Time, TimeDelta

from eascheduler.const import get_day_nr, get_month_nr
from eascheduler.helpers import HINT_CLOCK_BACKWARD, HINT_CLOCK_FORWARD, TimeReplacer, check_dst_handling


HINT_TIME: TypeAlias = dt_time | Time | str
HINT_TIMEDELTA: TypeAlias = dt_timedelta | TimeDelta | int | float | str
HINT_INSTANT: TypeAlias = dt_datetime | None | str | HINT_TIME, HINT_TIMEDELTA
HINT_NAME_OR_NR: TypeAlias = int | str | Iterable[int | str]


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


def _wrapped_range(start: int, stop: int, max_value: int) -> set[int]:
    if start < stop:
        return set(range(start, stop + 1))
    if start == stop:
        return {start}

    ret = set(range(start, max_value + 1))
    ret.update(range(1, stop + 1))
    return ret


def _parse_single_value(value: str | int, lookup: Callable[[str], int] | None,
                        min_value: int, max_value: int) -> int:
    if isinstance(value, int):
        int_value = value
    else:
        value = value.strip()
        if value.isdigit():
            int_value = int(value)
        else:
            if lookup is None:
                msg = f'Aliases can not be resolved and the provided value is not a valid number: {value}'
                raise ValueError(msg)
            int_value = lookup(value)

    if not min_value <= int_value <= max_value:
        msg = f'Value {int_value:d} is not in the range {min_value:d}-{max_value:d}'
        raise ValueError(msg)

    return int_value


def _parse_str_options(value: str, lookup: Callable[[str], int] | None,
                       min_value: int, max_value: int) -> set[int]:
    ret = set()
    if ',' in value:
        for part in value.split(','):
            ret.update(_parse_str_options(part, lookup, min_value, max_value))
    elif '-' in value:
        start_str, end_str = value.split('-', 1)
        ret.update(
            _wrapped_range(
                _parse_single_value(start_str, lookup, min_value, max_value),
                _parse_single_value(end_str, lookup, min_value, max_value),
                max_value
            )
        )
    else:
        ret.add(_parse_single_value(value, lookup, min_value, max_value))

    return ret


def _parse_values(values: Iterable[HINT_NAME_OR_NR], lookup: Callable[[str], int] | None,
                  min_value: int, max_value: int) -> set[int]:
    if not values:
        msg = 'No values provided.'
        raise ValueError(msg)

    ret = set()
    for value in values:
        if isinstance(value, int):
            ret.add(_parse_single_value(value, lookup, min_value, max_value))
        elif isinstance(value, str):
            ret.update(_parse_str_options(value, lookup, min_value, max_value))
        else:
            ret.update(_parse_values(value, lookup, min_value, max_value))

    return ret


def get_weekdays(*values: HINT_NAME_OR_NR) -> list[int]:
    return sorted(_parse_values(values, get_day_nr, 1, 7))


def get_days(*values: HINT_NAME_OR_NR) -> list[int]:
    return sorted(_parse_values(values, None, 1, 31))


def get_months(*values: HINT_NAME_OR_NR) -> list[int]:
    return sorted(_parse_values(values, get_month_nr, 1, 12))
