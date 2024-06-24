from whenever import UTCDateTime

from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import DateTimeJobControl
from eascheduler.jobs.base import STATUS_FINISHED, STATUS_PAUSED, STATUS_RUNNING
from eascheduler.jobs.job_datetime import DateTimeJob
from eascheduler.producers import IntervalProducer
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_eq():
    now = UTCDateTime.now().replace(microsecond=0)
    job1 = DateTimeJob(SyncExecutor(lambda: 1/0), IntervalProducer(now, 1))
    job2 = DateTimeJob(SyncExecutor(lambda: 1/0), IntervalProducer(now, 1))

    assert DateTimeJobControl(job1) == DateTimeJobControl(job1)
    assert DateTimeJobControl(job1) != DateTimeJobControl(job2)


async def test_datetime():

    s = AsyncScheduler()
    job = DateTimeJob(SyncExecutor(lambda: 1/0), IntervalProducer(UTCDateTime.now(), 1))
    job.link_scheduler(s)

    ctrl = DateTimeJobControl(job)

    assert job.status is STATUS_RUNNING
    ctrl.pause()
    assert job.status is STATUS_PAUSED
    ctrl.resume()
    assert job.status is STATUS_RUNNING
    ctrl.cancel()
    assert job.status is STATUS_FINISHED
