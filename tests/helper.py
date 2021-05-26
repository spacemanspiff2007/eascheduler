from typing import Union

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

from datetime import datetime as dt_datetime
from pendulum import datetime, instance, from_timestamp, UTC, DateTime
from pendulum import set_test_now as __set_test_now

from eascheduler.const import local_tz
from eascheduler.executors import AsyncExecutor


def utc_ts(year: int, month: int, day: int,
           hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0) -> float:
    return datetime(year, month, day, hour, minute, second, microsecond, tz=local_tz).in_timezone('UTC').timestamp()


def set_now(year: int, month: int, day: int,
            hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
            tz=local_tz):
    obj = datetime(year, month, day, hour, minute, second, microsecond=microsecond, tz=tz)
    if tz is not local_tz:
        obj = obj.in_timezone(local_tz)
    __set_test_now(obj)


class MockedAsyncExecutor(AsyncExecutor):
    def __init__(self, *args, **kwargs):
        self.mock = AsyncMock()
        super().__init__(self.mock, *args, **kwargs)


def mocked_executor(*args, **kwargs) -> MockedAsyncExecutor:
    return MockedAsyncExecutor(AsyncMock(*args, **kwargs))


def cmp_local(obj: Union[float, int, dt_datetime], local_dt: dt_datetime):
    if isinstance(obj, DateTime):
        assert obj.timezone
        cmp_dt = obj.in_tz(local_tz).naive()
    elif isinstance(obj, dt_datetime):
        cmp_dt = instance(obj, local_tz).astimezone(local_tz).naive()
    else:
        cmp_dt = from_timestamp(obj, tz=local_tz).naive()
    assert cmp_dt == local_dt, f'\n{cmp_dt}\n{local_dt}'


def cmp_utc(obj: Union[float, int, dt_datetime], local_dt: dt_datetime):
    if isinstance(obj, DateTime):
        assert obj.timezone
        cmp_dt = obj.in_tz(UTC).naive()
    elif isinstance(obj, dt_datetime):
        cmp_dt = instance(obj, local_tz).astimezone(local_tz).in_tz(UTC).naive()
    else:
        cmp_dt = from_timestamp(obj, tz=UTC).naive()
    assert cmp_dt == local_dt, f'\n{cmp_dt}\n{local_dt}'
