import asyncio

from whenever import Instant, TimeDelta

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_datetime import DateTimeJob
from eascheduler.producers import IntervalProducer
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_datetime() -> None:

    # we have to start the test at the beginning of a second, otherwise we sleep too long and get too much calls
    delay = 1 - Instant.now().to_system_tz().nanosecond / 100_000_000 - 0.1
    await asyncio.sleep(delay)

    calls = []

    def append() -> None:
        calls.append(Instant.now())

    now = Instant.now().to_system_tz().replace(nanosecond=0, disambiguate='raise').to_instant()
    producer = IntervalProducer(now, 1)
    s = AsyncScheduler()
    job = DateTimeJob(SyncExecutor(append), producer)
    job.link_scheduler(s)

    await asyncio.sleep(3.1)

    assert len(calls) == 3
    targets = [(now.add(seconds=i), now + TimeDelta(seconds=i + 0.1)) for i in range(1, 4)]

    for i, (low, high) in enumerate(targets):
        assert low <= calls[i] <= high
    assert job.status is STATUS_RUNNING

    job.job_pause()
    assert job.status is STATUS_PAUSED
    assert job.next_run is None

    job.job_resume()
    assert job.status is STATUS_RUNNING
    assert job.next_run == now.add(seconds=4)
