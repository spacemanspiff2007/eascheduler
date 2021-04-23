from datetime import date, datetime, time

import pytest
from pendulum import from_timestamp, UTC

from eascheduler import set_location
from eascheduler.const import SKIP_EXECUTION, local_tz
from eascheduler.executors import SyncExecutor
from eascheduler.jobs import DawnJob, DuskJob, SunriseJob, SunsetJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import set_now


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
async def test_calc(cls, jan_1: time, jan_30: time):
    set_location(52.5185537, 13.3758636, 43)
    s = AsyncScheduler()
    j = cls(s, SyncExecutor(lambda x: 1 / 0))
    s.add_job(j)

    set_now(2001, 1, 1, 1)
    j._schedule_next_run()
    # important - compare UTC timestamps!
    assert from_timestamp(j._next_run).naive() == datetime.combine(date(2001, 1, 1), jan_1)

    set_now(2001, 1, 30, 1)
    j._schedule_next_run()
    assert from_timestamp(j._next_run).naive() == datetime.combine(date(2001, 1, 30), jan_30)

    s.cancel_all()


@pytest.mark.asyncio
async def test_sunrise_skip():
    set_location(52.5185537, 13.3758636, 43)
    s = AsyncScheduler()
    j = SunriseJob(s, SyncExecutor(lambda x: 1 / 0))
    s.add_job(j)

    set_now(2001, 1, 1, 1)
    j._schedule_next_run()
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 1, 7, 15, 39)

    def skip_func(dt: datetime):
        if dt.day in [1, 2]:
            return SKIP_EXECUTION
        return dt

    j.boundary_func(skip_func)
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 3, 7, 15, 16)

    set_now(2001, 1, 1, 2)
    j._schedule_next_run()
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 3, 7, 15, 16)

    s.cancel_all()


@pytest.mark.asyncio
async def test_calc_advance():
    set_location(52.5185537, 13.3758636, 43)
    set_now(2001, 1, 1, 7, 10)
    s = AsyncScheduler()

    j = SunriseJob(s, SyncExecutor(lambda x: 1 / 0))
    s.add_job(j)
    j._schedule_next_run()
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 1, 7, 15, 39)

    j.latest(time(7, 5))
    assert from_timestamp(j._next_run).in_tz(local_tz).naive() == datetime(2001, 1, 2, 7, 5, 0)

    j.latest(None)
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 1, 7, 15, 39)

    set_now(2001, 1, 1, 7, 15, 39, tz=UTC)
    j._schedule_next_run()
    assert from_timestamp(j._next_run).naive() == datetime(2001, 1, 2, 7, 15, 29)

    j.cancel()
