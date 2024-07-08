from time import monotonic
from typing import Final, TypeVar

from whenever import LocalSystemDateTime, TimeDelta, UTCDateTime, ZonedDateTime


def get_german_as_utc(month=1, day=1, hour=0, minute=0, second=0, *, year=2001, microsecond=0) -> UTCDateTime:
    return ZonedDateTime(
        year, month, day, hour, minute=minute, second=second, microsecond=microsecond, tz='Europe/Berlin').as_utc()


def get_local_as_utc(month=1, day=1, hour=0, minute=0, second=0, *, year=2001, microsecond=0) -> UTCDateTime:
    return LocalSystemDateTime(year, month, day, hour, minute=minute, second=second, microsecond=microsecond).as_utc()


def cmp_utc_with_local(obj, *args, **kwargs):
    from_local = get_local_as_utc(*args, **kwargs)
    assert obj == from_local, f'\n{obj}\n{from_local}'
    return obj == from_local


def cmp_utc_with_german(obj, *args, **kwargs):
    from_german = get_local_as_utc(*args, **kwargs)
    assert obj == from_german, f'\n{obj}\n{from_german}'
    return obj == from_german


def get_ger_str(obj: UTCDateTime) -> str:
    return obj.as_zoned('Europe/Berlin').as_offset().common_iso8601()


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
        self._job.reset()
        self._last_reset = monotonic()
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
        assert target_lower < value, f'\n{target_lower}\n{value}'
        assert target_upper + offset_upper, f'\n{value}\n{target_upper}'
        return True

    if isinstance(value, (UTCDateTime, LocalSystemDateTime)) and isinstance(target, (UTCDateTime, LocalSystemDateTime)):
        target_lower = target - TimeDelta(seconds=offset_lower)
        target_upper = target + TimeDelta(seconds=offset_upper)
        assert target_lower < value, f'\n{target_lower}\n{value}'
        assert value < target_upper, f'\n{value}\n{target_upper}'
        return True

    raise ValueError()
