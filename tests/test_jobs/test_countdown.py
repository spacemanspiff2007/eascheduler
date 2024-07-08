import asyncio

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_countdown import CountdownJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import CountDownHelper


async def test_countdown():
    calls = CountDownHelper()

    s = AsyncScheduler()
    job = calls.link_job(CountdownJob(SyncExecutor(calls), 0.3))
    job.link_scheduler(s)

    calls.reset()
    assert job.status is STATUS_RUNNING

    for _ in range(10):
        await asyncio.sleep(0.01)
        calls.reset()

    calls.assert_not_called()
    await asyncio.sleep(0.35)

    calls.assert_called()
    assert job.status is STATUS_PAUSED


async def test_stop():
    calls = CountDownHelper()

    s = AsyncScheduler()
    job = calls.link_job(CountdownJob(SyncExecutor(calls), 0.1))
    job.link_scheduler(s)

    job.reset()
    for _ in range(10):
        await asyncio.sleep(0.005)
        calls.reset()

    job.job_pause()
    await asyncio.sleep(0.15)

    calls.assert_not_called()
    assert job.status is STATUS_PAUSED

    calls.reset()
    assert job.status is STATUS_RUNNING
    await asyncio.sleep(0.15)

    calls.assert_called()
    assert job.status is STATUS_PAUSED
