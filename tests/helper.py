try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

from pendulum import datetime
from pendulum import set_test_now as __set_test_now

from eascheduler.const import local_tz
from eascheduler.executors import AsyncExecutor


def utc_ts(year: int, month: int, day: int,
           hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0) -> float:
    return datetime(year, month, day, hour, minute, second, microsecond, tz=local_tz).in_timezone('UTC').timestamp()


def set_now(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0):
    obj = datetime(year, month, day, hour, minute, second, microsecond=microsecond, tz=local_tz)
    __set_test_now(obj)


class MockedAsyncExecutor(AsyncExecutor):
    def __init__(self, *args, **kwargs):
        self.mock = AsyncMock()
        super().__init__(self.mock, *args, **kwargs)


def mocked_executor(*args, **kwargs) -> MockedAsyncExecutor:
    return MockedAsyncExecutor(AsyncMock(*args, **kwargs))
