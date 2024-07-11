import asyncio

from whenever import SystemDateTime, TimeDelta

from eascheduler.builder import JobBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import assert_called_at


async def test_onetime():
    calls = []

    def append():
        calls.append(SystemDateTime.now())

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    builder.once(TimeDelta(seconds=0.01), append)
    target = SystemDateTime.now() + TimeDelta(seconds=0.01)

    await asyncio.sleep(0.02)

    assert_called_at(calls, target)
