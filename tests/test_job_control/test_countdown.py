import asyncio
from time import monotonic

from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import CountdownJobControl
from eascheduler.jobs.base import STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_countdown import CountdownJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_eq():
    job1 = CountdownJob(SyncExecutor(lambda: 1/0))
    job2 = CountdownJob(SyncExecutor(lambda: 1/0))

    assert CountdownJobControl(job1) == CountdownJobControl(job1)
    assert CountdownJobControl(job1) != CountdownJobControl(job2)


async def test_countdown():

    last_reset = 0
    calls = []

    def append():
        calls.append(monotonic() - last_reset)

    s = AsyncScheduler()
    job = CountdownJob(SyncExecutor(append))
    job.link_scheduler(s)

    ctrl = CountdownJobControl(job)
    ctrl.set_countdown(0.3)

    ctrl.reset()
    assert job.status is STATUS_RUNNING

    for _ in range(10):
        await asyncio.sleep(0.01)
        ctrl.reset()
        last_reset = monotonic()

    assert calls == []
    await asyncio.sleep(0.35)

    assert len(calls) == 1
    assert 0.25 < calls[0] < 0.35
    assert job.status is STATUS_PAUSED


async def test_stop():

    last_reset = 0
    calls = []

    def append():
        calls.append(monotonic() - last_reset)

    s = AsyncScheduler()
    job = CountdownJob(SyncExecutor(append))
    job.link_scheduler(s)

    ctrl = CountdownJobControl(job)
    ctrl.set_countdown(0.1)

    ctrl.reset()
    for _ in range(10):
        await asyncio.sleep(0.005)
        ctrl.reset()

    ctrl.stop()
    await asyncio.sleep(0.15)

    assert calls == []
    assert job.status is STATUS_PAUSED

    ctrl.reset()
    last_reset = monotonic()
    assert job.status is STATUS_RUNNING
    await asyncio.sleep(0.15)

    assert len(calls) == 1
    assert 0.05 < calls[0] < 0.15
    assert job.status is STATUS_PAUSED
