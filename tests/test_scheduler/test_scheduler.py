import asyncio
from time import monotonic

from pendulum import DateTime

from eascheduler.const import local_tz
from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_FINISHED
from eascheduler.jobs.job_onetime import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_scheduler():

    calls = []

    def append():
        calls.append(1)
    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(append), DateTime.now(tz=local_tz).add(seconds=0.01))
    job.link_scheduler(s)

    await asyncio.sleep(0.1)

    assert calls == [1]
    assert s.timer is None
    assert job.status is STATUS_FINISHED


async def test_scheduler_update():

    call_duration = 99

    def append(t):
        nonlocal call_duration
        call_duration = monotonic() - t

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(append, (monotonic(), )), DateTime.now(tz=local_tz).add(seconds=0.01))
    job.link_scheduler(s)

    job.loop_time = monotonic() + 0.02
    s.update_job(job)

    await asyncio.sleep(0.1)

    assert 0.02 < call_duration < 0.04
    assert s.timer is None


async def test_scheduler_repr():

    s = AsyncScheduler()
    assert repr(s) == '<AsyncScheduler jobs=0 next_run=None>'

    job = OneTimeJob(SyncExecutor(lambda: None), DateTime.now(tz=local_tz).add(seconds=0.01))
    job.link_scheduler(s)
    assert repr(s) == '<AsyncScheduler jobs=1 next_run=0.010s>'

    s.remove_job(job)
    assert repr(s) == '<AsyncScheduler jobs=0 next_run=None>'
