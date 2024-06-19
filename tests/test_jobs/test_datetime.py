import asyncio

from pendulum import DateTime

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_RUNNING, STATUS_STOPPED
from eascheduler.jobs.job_datetime import DateTimeJob
from eascheduler.producers import IntervalProducer
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_datetime():

    calls = []

    def append():
        calls.append(DateTime.now())

    now = DateTime.now().replace(microsecond=0)
    producer = IntervalProducer(now, 1)
    s = AsyncScheduler()
    job = DateTimeJob(SyncExecutor(append), producer)
    job.link_scheduler(s)

    await asyncio.sleep(3.1)

    assert len(calls) == 3
    targets = [(now.add(seconds=i), now.add(seconds=i + 0.1)) for i in range(1, 4)]

    for i, (low, high) in enumerate(targets):
        assert low <= calls[i] <= high

    assert job.status is STATUS_RUNNING

    job.job_stop()
    assert job.status is STATUS_STOPPED
