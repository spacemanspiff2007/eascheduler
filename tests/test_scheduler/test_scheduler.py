import asyncio
from time import monotonic

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.job_onetime import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_scheduler():

    calls = []

    def append():
        calls.append(1)

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(append))
    job.next_time = monotonic() + 0.01
    s.add_job(job)

    await asyncio.sleep(0.1)

    assert calls == [1]
    assert s.timer is None
