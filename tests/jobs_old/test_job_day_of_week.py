from datetime import datetime, time, timedelta
from functools import partial

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.errors import UnknownWeekdayError
from eascheduler.old_executors import SyncExecutor
from eascheduler.old_jobs.job_day_of_week import DayOfWeekJob
from eascheduler.old_schedulers import AsyncScheduler
from tests.helper import set_now, utc_ts


async def test_workdays(async_scheduler: AsyncScheduler):
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    j = DayOfWeekJob(async_scheduler, lambda x: x)
    async_scheduler.add_job(j)
    async_scheduler.add_job(dummy)

    j.time(time(11))
    j.weekdays('workdays')

    now = partial(set_now, 2001, 1, hour=11, microsecond=1)

    def skip_func(dt: datetime):
        if dt.day == 4:
            return SKIP_EXECUTION
        return dt

    for skip in (None, skip_func):
        days = [1, 2,  3,  4,  5,
                8, 9, 10, 11, 12,
                15]

        set_now(2001, 1, 1, 10)

        if skip:
            j.boundary_func(skip)
            days.remove(4)

        for day in days:
            j._schedule_next_run()
            assert j.get_next_run() == datetime(2001, 1, day, 11)
            now(day)

    async_scheduler.cancel_all()


async def test_weekends(async_scheduler: AsyncScheduler):
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    j = DayOfWeekJob(async_scheduler, lambda x: x)
    async_scheduler.add_job(j)
    async_scheduler.add_job(dummy)

    j.time(time(11))
    j.weekdays('weekend')

    now = partial(set_now, 2001, 1, hour=11, microsecond=1)

    def skip_func(dt: datetime):
        if dt.day == 13:
            return SKIP_EXECUTION
        return dt

    for skip in (None, skip_func):
        days = [6, 7, 13, 14, 20, 21]

        set_now(2001, 1, 1, 10)

        if skip:
            j.boundary_func(skip)
            days.remove(13)

        for day in days:
            j._schedule_next_run()
            assert j.get_next_run() == datetime(2001, 1, day, 11)
            now(day)

    async_scheduler.cancel_all()


async def test_day(async_scheduler: AsyncScheduler):
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    j = DayOfWeekJob(async_scheduler, lambda x: x)
    async_scheduler.add_job(j)

    now = partial(set_now, 2001, 1, hour=12, microsecond=1)
    j.time(time(12))
    j.weekdays('mo')

    now(1, hour=11)
    j._schedule_next_run()
    assert j.get_next_run() == datetime(2001, 1, 1, 12)
    now(1)
    j._schedule_next_run()
    assert j.get_next_run() == datetime(2001, 1, 8, 12)
    now(8)
    j._schedule_next_run()
    assert j.get_next_run() == datetime(2001, 1, 15, 12)

    j.weekdays(['mo', 'di'])

    now(1, hour=11)
    j._schedule_next_run()

    for d in (1, 2, 8, 9, 15, 16):
        assert j.get_next_run() == datetime(2001, 1, d, 12)
        now(d)
        j._schedule_next_run()

    j.cancel()


async def test_day_exception(async_scheduler: AsyncScheduler):
    dummy = DayOfWeekJob(async_scheduler, lambda x: x)
    with pytest.raises(UnknownWeekdayError) as e:
        dummy.weekdays('asdf')
    assert str(e.value).startswith('Unknown day "asdf"!')


async def test_negative_offset(async_scheduler: AsyncScheduler):

    j = DayOfWeekJob(async_scheduler, SyncExecutor(lambda: 1))
    j.time(time(12))
    j.offset(timedelta(minutes=-30))
    j._next_run_base = utc_ts(2001, 1, 1, 12)
    j._next_run      = utc_ts(2001, 1, 1, 11, 30)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(11, 30)

    j._execute()

    assert j._next_run_base == utc_ts(2001, 1, 2, 12)
    assert j._next_run      == utc_ts(2001, 1, 2, 11, 30)
