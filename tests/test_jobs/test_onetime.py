import asyncio

from pendulum import DateTime

from eascheduler.const import local_tz
from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_FINISHED
from eascheduler.jobs.job_onetime import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_onetime():

    calls = []

    def append():
        calls.append(1)

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(append), DateTime.now(tz=local_tz).add(seconds=0.01))
    job.link_scheduler(s)

    await asyncio.sleep(0.05)

    assert calls == [1]
    assert job.status is STATUS_FINISHED
