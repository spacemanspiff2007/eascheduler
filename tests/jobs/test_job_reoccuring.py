from asyncio import sleep
from datetime import datetime, timedelta
from functools import partial

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.executors import SyncExecutor
from eascheduler.jobs import ReoccurringJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, set_now, utc_ts


@pytest.mark.asyncio
async def test_remove(async_scheduler: AsyncScheduler):

    j = ReoccurringJob(async_scheduler, lambda x: x)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=0)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(1, microsecond=0)

    async_scheduler.add_job(j)
    j.interval(5)

    now(11)
    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12))

    now(12)
    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12, 0, 5))
    now(12, 0, 5)

    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12, 0, 10))



@pytest.mark.asyncio
async def test_skip(async_scheduler: AsyncScheduler):

    j = ReoccurringJob(async_scheduler, lambda x: x)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=0)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(1, microsecond=0)

    def skip_func(dt: datetime):
        if dt.second == 10:
            return SKIP_EXECUTION
        return dt

    async_scheduler.add_job(j)
    j.interval(5)
    j.boundary_func(skip_func)

    now(11)
    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12))

    now(12)
    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12, 0, 5))
    now(12, 0, 5)

    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12, 0, 15))
    now(12, 0, 15)

    j._schedule_next_run()
    cmp_local(j._next_run, datetime(2001, 1, 1, 12, 0, 20))


@pytest.mark.asyncio
async def test_func_exception(async_scheduler: AsyncScheduler, caught_exceptions):
    async def bla():
        pass

    calls = 0

    def func(arg):
        nonlocal calls
        if calls:
            1 / 0
        calls += 1
        return arg

    set_now(2001, 1, 1, 7, 10)

    j1 = ReoccurringJob(async_scheduler, SyncExecutor(lambda: 1))
    j1._schedule_first_run(999)
    j1.interval(999)

    j = ReoccurringJob(async_scheduler, SyncExecutor(lambda: 1))
    j._schedule_first_run(0.00001)
    j.interval(999)

    j.boundary_func(func)

    set_now(2001, 1, 1, 7, 10, 1)
    await sleep(0.3)

    # ensure that the worker is still running
    assert async_scheduler.worker is not None

    # ensure that the exception got caught
    assert len(caught_exceptions) == 1
    assert str(caught_exceptions[0]) == 'division by zero'
    caught_exceptions.clear()


@pytest.mark.asyncio
async def test_negative_offset(async_scheduler: AsyncScheduler):

    j = ReoccurringJob(async_scheduler, SyncExecutor(lambda: 1))
    j.interval(3600)
    j.offset(timedelta(minutes=-30))
    j._next_run_base = utc_ts(2001, 1, 1, 12)
    j._next_run      = utc_ts(2001, 1, 1, 11, 30)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(11, 30)

    j._execute()

    assert j._next_run_base == utc_ts(2001, 1, 1, 13)
    assert j._next_run      == utc_ts(2001, 1, 1, 12, 30)
