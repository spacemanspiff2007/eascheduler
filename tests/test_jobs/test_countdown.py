import asyncio
from time import monotonic

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_FINISHED, STATUS_STOPPED, STATUS_RUNNING
from eascheduler.jobs.job_countdown import CountdownJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_countdown():

    last_reset = 0
    calls = []

    def append():
        calls.append(monotonic() - last_reset)

    s = AsyncScheduler()
    job = CountdownJob(SyncExecutor(append))
    job.countdown(0.3)
    job.link_scheduler(s)

    job.reset()
    assert job.status is STATUS_RUNNING

    for _ in range(10):
        await asyncio.sleep(0.01)
        job.reset()
        last_reset = monotonic()

    assert calls == []
    await asyncio.sleep(0.35)

    assert len(calls) == 1
    assert 0.25 < calls[0] < 0.35
    assert job.status is STATUS_STOPPED


async def test_stop():

    last_reset = 0
    calls = []

    def append():
        calls.append(monotonic() - last_reset)

    s = AsyncScheduler()
    job = CountdownJob(SyncExecutor(append))
    job.countdown(0.1)
    job.link_scheduler(s)

    job.reset()
    for _ in range(10):
        await asyncio.sleep(0.005)
        job.reset()

    job.job_stop()
    await asyncio.sleep(0.15)

    assert calls == []
    assert job.status is STATUS_STOPPED

    job.reset()
    last_reset = monotonic()
    assert job.status is STATUS_RUNNING
    await asyncio.sleep(0.15)

    assert len(calls) == 1
    assert 0.05 < calls[0] < 0.15
    assert job.status is STATUS_STOPPED
