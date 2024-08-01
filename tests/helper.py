from enum import Enum
from time import monotonic
from typing import Final, Literal, TypeVar, Union, get_args, get_origin

import pytest
from whenever import Instant, SystemDateTime, TimeDelta, ZonedDateTime


def get_german_as_instant(month=1, day=1, hour=0, minute=0, second=0, *, year=2001, microsecond=0) -> Instant:
    return ZonedDateTime(
        year, month, day, hour, minute=minute, second=second, nanosecond=microsecond * 1000, tz='Europe/Berlin'
    ).instant()


def get_system_as_instant(month=1, day=1, hour=0, minute=0, second=0, *, year=2001, microsecond=0) -> Instant:
    return SystemDateTime(
        year, month, day, hour, minute=minute, second=second, nanosecond=microsecond * 1000
    ).instant()


def get_ger_str(obj: Instant) -> str:
    return obj.to_tz('Europe/Berlin').to_fixed_offset().format_common_iso()


T = TypeVar('T')

# https://docs.python.org/3/library/asyncio-platforms.html
CLOCK_GRANULARITY: Final = 0.0156


class CountDownHelper:
    def __init__(self):
        self._calls: list[float] = []
        self._last_reset = monotonic()
        self._job = None

    def link_job(self, job: T) -> T:
        self._job = job
        return job

    def __call__(self):
        self._calls.append(monotonic() - self._last_reset)

    def reset(self):
        self._last_reset = monotonic()
        self._job.reset()
        return self

    def assert_not_called(self):
        assert not self._calls
        return self

    def assert_called(self, length: int = 1):
        assert len(self._calls) == length

        job = self._job
        if hasattr(job, '_job'):
            job = job._job

        for value in self._calls:
            assert_called_at(value, job._seconds)
        return self


def _fmt_diff(value: TimeDelta | float) -> str:
    if isinstance(value, TimeDelta):
        value = value.in_seconds()
    if abs(value) > 0.02:
        return f'{value:.3f}s'
    value *= 1000
    return f'{value:.3f}ms'


def assert_called_at(value, target):
    offset_lower = 0
    offset_upper = CLOCK_GRANULARITY * 1.5

    # unpack list with one entry
    if isinstance(value, (list, tuple)):
        assert len(value) == 1
        value = value[0]

    if isinstance(value, float) and isinstance(target, float):
        target_lower = target - offset_lower
        target_upper = target + offset_upper
        assert target_lower < value, f'\n{target_lower}\n{value}  {_fmt_diff(value-target_lower):s}'
        assert value < target_upper, f'\n{value}  {_fmt_diff(value-target_upper):s}\n{target_upper}'
        return True

    if isinstance(value, (Instant, SystemDateTime)) and isinstance(target, (Instant, SystemDateTime)):
        target_lower = target - TimeDelta(seconds=offset_lower)
        target_upper = target + TimeDelta(seconds=offset_upper)
        assert target_lower < value, f'\n{target_lower}\n{value}  {_fmt_diff(value-target_lower):s}'
        assert value < target_upper, f'\n{value}  {_fmt_diff(value-target_upper):s}\n{target_upper}'
        return True

    raise ValueError()


def assert_literal_values_in_enum(obj):
    assert get_origin(obj) is Union
    a, b = get_args(obj)

    enum = a if hasattr(a, '__members__') else b
    literal = b if hasattr(a, '__members__') else a

    # cast all values to an enum
    values_literal = set(get_args(literal))
    values_enum = {v.value for v in enum}

    assert values_literal == values_enum, f'\n{values_literal}\n{values_enum}'

    for value in values_literal:
        enum(value)


def test_assert_literal_values_in_enum():
    class TestEnum(Enum):
        A = 1
        B = 2

    with pytest.raises(AssertionError):
        assert_literal_values_in_enum(Literal[1] | TestEnum)
    with pytest.raises(AssertionError):
        assert_literal_values_in_enum(Literal[1, 2, 3] | TestEnum)

    assert_literal_values_in_enum(Literal[1, 2] | TestEnum)
