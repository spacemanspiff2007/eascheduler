from datetime import datetime as dt_datetime

from whenever import Instant, SystemDateTime, TimeDelta

from eascheduler.executor.base import SyncExecutor
from eascheduler.job_control import OneTimeJobControl
from eascheduler.jobs.base import STATUS_FINISHED
from eascheduler.jobs.job_onetime import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler
from tests.helper import AlwaysError


async def test_eq() -> None:
    job1 = OneTimeJob(SyncExecutor(AlwaysError()), Instant.now() + TimeDelta(seconds=0.01))
    job2 = OneTimeJob(SyncExecutor(AlwaysError()), Instant.now() + TimeDelta(seconds=0.01))

    assert OneTimeJobControl(job1) == OneTimeJobControl(job1)
    assert OneTimeJobControl(job1) != OneTimeJobControl(job2)


async def test_onetime() -> None:

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(AlwaysError()), Instant.now() + TimeDelta(seconds=0.01))
    job.link_scheduler(s)

    OneTimeJobControl(job).cancel()
    assert job.status is STATUS_FINISHED


async def test_base_properties() -> None:

    now = SystemDateTime.now().add(seconds=1)

    s = AsyncScheduler()
    job = OneTimeJob(SyncExecutor(AlwaysError()), now.instant())
    job.link_scheduler(s)

    ctrl = OneTimeJobControl(job)
    assert ctrl.next_run_datetime == dt_datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second,
        microsecond=now.nanosecond // 1000
    )

    ctrl.cancel()
    assert ctrl.status == 'finished'

    assert ctrl.next_run_datetime is None
    assert ctrl.next_run_datetime is None
