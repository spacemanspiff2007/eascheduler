import asyncio

from eascheduler.builder import JobBuilder
from eascheduler.executor.base import SyncExecutor
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import CountDownHelper


async def test_countdown():

    calls = CountDownHelper()

    builder = JobBuilder(AsyncScheduler(), SyncExecutor)
    job = calls.link_job(builder.countdown(0.1, calls))

    calls.reset()
    assert job.status.is_running

    for _ in range(10):
        await asyncio.sleep(0.02)
        calls.reset()

    calls.assert_not_called()
    await asyncio.sleep(0.15)

    calls.assert_called()
    assert job.status.is_paused
