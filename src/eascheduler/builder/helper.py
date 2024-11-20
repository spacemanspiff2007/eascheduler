from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date as dt_date
from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import Any, Final, Generic, TypeAlias, TypeVar

from whenever import Date, Instant, SystemDateTime, Time, TimeDelta

from eascheduler.const import get_day_nr, get_month_nr
from eascheduler.helpers import HINT_CLOCK_BACKWARD, HINT_CLOCK_FORWARD, TimeReplacer, check_dst_handling


HINT_TIME: TypeAlias = dt_time | Time | str
HINT_TIMEDELTA: TypeAlias = dt_timedelta | TimeDelta | int | float | str
HINT_POS_TIMEDELTA: TypeAlias = HINT_TIMEDELTA
HINT_INSTANT: TypeAlias = dt_datetime | None | str | HINT_TIME | HINT_TIMEDELTA | SystemDateTime
HINT_NAME_OR_NR: TypeAlias = int | str | Iterable[int | str]
HINT_DATE: TypeAlias = dt_date | dt_datetime | str | None | Date | SystemDateTime | Instant


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


def get_pos_timedelta_secs(value: HINT_POS_TIMEDELTA) -> float:
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


def get_pydate(value: HINT_DATE) -> dt_date:  # noqa: PLR0911

    match value:
        case dt_datetime():
            return value.date()
        case dt_date():
            return value

        case None:
            return SystemDateTime.now().date().py_date()
        case str():
            return Date.parse_common_iso(value).py_date()

        case Date():
            return value.py_date()
        case SystemDateTime():
            return value.date().py_date()
        case Instant():
            return value.to_system_tz().date().py_date()

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
            if value.tzinfo is not None:
                return SystemDateTime.from_py_datetime(value).instant()
            # We assume it's the system datetime because that's what datetime is normally used for
            return SystemDateTime(value.year, value.month, value.day, value.hour, value.minute,
                                  value.second, nanosecond=value.microsecond * 1_000).instant()
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
            new = new.add(hours=24)
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


TYPE_OUT = TypeVar('TYPE_OUT')


class BuilderTypeValidator(Generic[TYPE_OUT]):
    __slots__ = ('type_in', 'type_out', 'var_name')

    def __init__(self, type_in: type[object], type_out: type[TYPE_OUT], var_name: str) -> None:
        self.type_in: Final = type_in
        self.type_out: Final = type_out
        self.var_name: Final = var_name

    def __call__(self, obj: Any) -> TYPE_OUT:
        if not isinstance(obj, self.type_in):
            msg = f'Expected type {self.type_in.__name__}, got {obj} ({type(obj).__name__})'
            raise TypeError(msg)

        obj = getattr(obj, self.var_name)
        if not isinstance(obj, self.type_out):
            msg = f'Expected an instance of {self.type_out.__name__}, got {obj} ({type(obj).__name__})'
            raise TypeError(msg)

        return obj

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.type_in.__name__}, {self.type_out.__name__}, {self.var_name})'
