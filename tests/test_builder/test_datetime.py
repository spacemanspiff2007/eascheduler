import asyncio

from whenever import SystemDateTime, Time, TimeDelta

from eascheduler.builder import FilterBuilder, JobBuilder, TriggerBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import assert_called_at


async def test_datetime():
    calls = []

    def append():
        calls.append(SystemDateTime.now())

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    builder.at(
        TriggerBuilder.time(Time(8)),
        append
    )


    await asyncio.sleep(0.02)

    assert_called_at(calls, target)
