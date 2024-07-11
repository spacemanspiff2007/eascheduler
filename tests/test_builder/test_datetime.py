import asyncio

from whenever import SystemDateTime

from eascheduler.builder import JobBuilder, TriggerBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import assert_called_at


async def test_datetime():
    calls = []

    def append():
        calls.append(SystemDateTime.now())

    now = SystemDateTime.now()
    dst = now.add(seconds=1).replace(nanosecond=0, disambiguate='raise')

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    builder.at(
        TriggerBuilder.time(dst.time()),
        append
    )

    await asyncio.sleep((dst - now).in_seconds() + 0.01)

    assert_called_at(calls, dst)
