from datetime import time, datetime
from functools import partial

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.jobs.job_day_of_week import DayOfWeekJob
from eascheduler.schedulers import AsyncScheduler
from eascheduler.errors import UnknownWeekdayError
from tests.helper import set_now


@pytest.mark.asyncio
async def test_workdays():
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    s = AsyncScheduler()
    j = DayOfWeekJob(s, lambda x: x)
    s.add_job(j)
    s.add_job(dummy)

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

    s.cancel_all()


@pytest.mark.asyncio
async def test_weekends():
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    s = AsyncScheduler()
    j = DayOfWeekJob(s, lambda x: x)
    s.add_job(j)
    s.add_job(dummy)

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

    s.cancel_all()


@pytest.mark.asyncio
async def test_day():
    dummy = DayOfWeekJob(None, lambda x: x)
    dummy._next_run = 0

    s = AsyncScheduler()
    j = DayOfWeekJob(s, lambda x: x)
    s.add_job(j)

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


@pytest.mark.asyncio
async def test_day_exception():
    s = AsyncScheduler()
    dummy = DayOfWeekJob(s, lambda x: x)
    with pytest.raises(UnknownWeekdayError) as e:
        dummy.weekdays('asdf')
    assert str(e.value).startswith('Unknown day "asdf"!')
