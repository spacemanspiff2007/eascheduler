from datetime import date, datetime, time
from datetime import timedelta

import pytest
from pendulum import UTC

from eascheduler import set_location
from eascheduler.const import SKIP_EXECUTION
from eascheduler.executors import SyncExecutor
from eascheduler.jobs import DawnJob, DuskJob, SunriseJob, SunsetJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_utc, cmp_local, set_now


@pytest.mark.parametrize(
    'cls,jan_1,jan_30',
    [
        (DawnJob,    time( 6, 34,  4), time( 6, 12,  6)),
        (SunriseJob, time( 7, 15, 39), time( 6, 49, 53)),
        (SunsetJob,  time(15,  4, 48), time(15, 50, 24)),
        (DuskJob,    time(15, 46, 23), time(16, 28, 14)),
    ]
)
@pytest.mark.asyncio
async def test_calc(async_scheduler: AsyncScheduler, cls, jan_1: time, jan_30: time):
    set_location(52.5185537, 13.3758636, 43)

    j = cls(async_scheduler, SyncExecutor(lambda x: 1 / 0))
    async_scheduler.add_job(j)

    set_now(2001, 1, 1, 1)
    j._schedule_next_run()
    # important - compare UTC timestamps!
    cmp_utc(j._next_run, datetime.combine(date(2001, 1, 1), jan_1))

    set_now(2001, 1, 30, 1)
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime.combine(date(2001, 1, 30), jan_30))


@pytest.mark.asyncio
async def test_sunrise_skip(async_scheduler: AsyncScheduler):
    set_location(52.5185537, 13.3758636, 43)

    j = SunriseJob(async_scheduler, SyncExecutor(lambda x: 1 / 0))
    async_scheduler.add_job(j)

    set_now(2001, 1, 1, 1)
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime(2001, 1, 1, 7, 15, 39))

    def skip_func(dt: datetime):
        if dt.day in [1, 2]:
            return SKIP_EXECUTION
        return dt

    j.boundary_func(skip_func)
    cmp_utc(j._next_run, datetime(2001, 1, 3, 7, 15, 16))

    set_now(2001, 1, 1, 2)
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime(2001, 1, 3, 7, 15, 16))


@pytest.mark.asyncio
async def test_calc_advance(async_scheduler: AsyncScheduler):
    set_location(52.5185537, 13.3758636, 43)
    set_now(2001, 1, 1, 7, 10)

    j = SunriseJob(async_scheduler, SyncExecutor(lambda x: 1 / 0))
    async_scheduler.add_job(j)
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime(2001, 1, 1, 7, 15, 39))

    j.latest(time(7, 5))
    cmp_local(j._next_run, datetime(2001, 1, 2, 7, 5, 0))

    j.latest(None)
    cmp_utc(j._next_run, datetime(2001, 1, 1, 7, 15, 39))

    set_now(2001, 1, 1, 7, 15, 39, tz=UTC)
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime(2001, 1, 2, 7, 15, 29))

    j.cancel()


@pytest.mark.asyncio
async def test_negative_offset(async_scheduler: AsyncScheduler):

    set_location(52.5185537, 13.3758636, 43)
    set_now(2001, 1, 1, 6, tz=UTC)

    j = SunriseJob(async_scheduler, SyncExecutor(lambda: 1))
    j._schedule_next_run()
    cmp_utc(j._next_run, datetime(2001, 1, 1, 7, 15, 39))

    j.offset(timedelta(minutes=-30))
    cmp_utc(j._next_run, datetime(2001, 1, 1, 6, 45, 39))

    j._execute()

    cmp_utc(j._next_run, datetime(2001, 1, 2, 6, 45, 29))
