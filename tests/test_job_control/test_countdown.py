import asyncio
from time import monotonic

from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import CountdownJobControl
from eascheduler.jobs.base import STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_countdown import CountdownJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import CountDownHelper


async def test_eq():
    job1 = CountdownJob(SyncExecutor(lambda: 1/0), 1)
    job2 = CountdownJob(SyncExecutor(lambda: 1/0), 1)

    assert CountdownJobControl(job1) == CountdownJobControl(job1)
    assert CountdownJobControl(job1) != CountdownJobControl(job2)


async def test_countdown():
    calls = CountDownHelper()

    s = AsyncScheduler()
    job = CountdownJob(SyncExecutor(calls), 1)
    job.link_scheduler(s)

    ctrl = calls.link_job(CountdownJobControl(job))
    ctrl.set_countdown(0.3)

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
    job = CountdownJob(SyncExecutor(calls), 1)
    job.link_scheduler(s)

    ctrl = calls.link_job(CountdownJobControl(job))
    ctrl.set_countdown(0.1)

    ctrl.reset()
    for _ in range(10):
        await asyncio.sleep(0.005)
        ctrl.reset()

    ctrl.stop()
    await asyncio.sleep(0.15)

    assert calls.assert_not_called()
    assert job.status is STATUS_PAUSED

    calls.reset()
    assert job.status is STATUS_RUNNING
    await asyncio.sleep(0.15)

    calls.assert_called()
    assert job.status is STATUS_PAUSED
