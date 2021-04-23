from asyncio import sleep
from datetime import datetime
from functools import partial

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.executors import SyncExecutor
from eascheduler.jobs import ReoccurringJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, set_now, utc_ts


@pytest.mark.asyncio
async def test_remove():

    s = AsyncScheduler()
    j = ReoccurringJob(s, lambda x: x)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=0)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(1, microsecond=0)

    s.add_job(j)
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

    s.cancel_all()


@pytest.mark.asyncio
async def test_skip():

    s = AsyncScheduler()
    j = ReoccurringJob(s, lambda x: x)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=0)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(1, microsecond=0)

    def skip_func(dt: datetime):
        if dt.second == 10:
            return SKIP_EXECUTION
        return dt

    s.add_job(j)
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

    s.cancel_all()


@pytest.mark.asyncio
async def test_func_exception(caught_exceptions):
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

    s = AsyncScheduler()
    j1 = ReoccurringJob(s, SyncExecutor(lambda: 1))
    j1._schedule_first_run(999)
    j1.interval(999)

    j = ReoccurringJob(s, SyncExecutor(lambda: 1))
    j._schedule_first_run(None)
    j.interval(999)

    j.boundary_func(func)

    set_now(2001, 1, 1, 7, 10, 1)
    await sleep(0.3)

    # ensure that the worker is still running
    assert s.worker is not None

    # ensure that the exception got caught
    assert len(caught_exceptions) == 1
    assert str(caught_exceptions[0]) == 'division by zero'
    caught_exceptions.clear()

    s.cancel_all()
