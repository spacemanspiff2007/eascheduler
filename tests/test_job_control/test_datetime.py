from whenever import Instant, SystemDateTime

from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import DateTimeJobControl
from eascheduler.jobs.base import STATUS_FINISHED, STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_datetime import DateTimeJob
from eascheduler.producers import IntervalProducer
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import AlwaysError


async def test_eq() -> None:
    now = SystemDateTime.now().replace(nanosecond=0, disambiguate='raise').to_instant()
    job1 = DateTimeJob(SyncExecutor(AlwaysError()), IntervalProducer(now, 1))
    job2 = DateTimeJob(SyncExecutor(AlwaysError()), IntervalProducer(now, 1))

    assert DateTimeJobControl(job1) == DateTimeJobControl(job1)
    assert DateTimeJobControl(job1) != DateTimeJobControl(job2)


async def test_datetime() -> None:

    s = AsyncScheduler()
    job = DateTimeJob(SyncExecutor(AlwaysError()), IntervalProducer(Instant.now(), 1))
    job.link_scheduler(s)

    ctrl = DateTimeJobControl(job)

    assert job.status is STATUS_RUNNING
    ctrl.pause()
    assert job.status is STATUS_PAUSED
    ctrl.resume()
    assert job.status is STATUS_RUNNING
    ctrl.cancel()
    assert job.status is STATUS_FINISHED
