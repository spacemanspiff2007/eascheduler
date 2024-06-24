from whenever import TimeDelta, UTCDateTime

from eascheduler.const import local_tz
from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import OneTimeJobControl
from eascheduler.jobs.base import STATUS_FINISHED
from eascheduler.jobs.job_onetime import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_eq():
    job1 = OneTimeJob(SyncExecutor(lambda: 1/0), UTCDateTime.now() + TimeDelta(seconds=0.01))
    job2 = OneTimeJob(SyncExecutor(lambda: 1/0), UTCDateTime.now() + TimeDelta(seconds=0.01))

    assert OneTimeJobControl(job1) == OneTimeJobControl(job1)
    assert OneTimeJobControl(job1) != OneTimeJobControl(job2)


async def test_onetime():

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(lambda: 1/0), UTCDateTime.now() + TimeDelta(seconds=0.01))
    job.link_scheduler(s)

    OneTimeJobControl(job).cancel()
    assert job.status is STATUS_FINISHED


async def test_base_properties():

    target = UTCDateTime.now() + TimeDelta(seconds=0.01)
    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(lambda: 1/0), target)
    job.link_scheduler(s)

    ctrl = OneTimeJobControl(job)
    assert ctrl.next_run == target.naive()
    assert ctrl.next_run_tz == target

    ctrl.cancel()
    assert ctrl.status == 'finished'

    assert ctrl.next_run is None
    assert ctrl.next_run_tz is None
    assert ctrl.last_run is None
    assert ctrl.last_run_tz is None
