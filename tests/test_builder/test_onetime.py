import asyncio

from whenever import TimeDelta, ZonedDateTime

from eascheduler.builder import JobBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import assert_called_at


async def test_onetime() -> None:
    calls = []

    def append() -> None:
        calls.append(ZonedDateTime.now_in_system_tz())

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    builder.once(TimeDelta(seconds=0.01), append)
    target = ZonedDateTime.now_in_system_tz() + TimeDelta(seconds=0.01)

    await asyncio.sleep(0.02)

    assert_called_at(calls, target)
