import asyncio
from datetime import datetime, timedelta

import pytest

from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.executors import SyncExecutor
from eascheduler.jobs.job_one_time import OneTimeJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, mocked_executor, set_now, utc_ts, sleep


async def test_remove():

    s = AsyncScheduler()
    e = mocked_executor()
    j = OneTimeJob(s, e)
    set_now(2001, 1, 1, 12, 0, 0)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=100_000)
    j._set_next_run(j._next_run_base)

    e.mock.assert_not_called()

    await sleep(0.05)
    set_now(2001, 1, 1, 12, microsecond=100_001)
    await sleep(0.01)

    e.mock.assert_called_once()

    assert j not in s.jobs
    assert j not in s.job_objs
    assert j._parent is None

    with pytest.raises(JobAlreadyCanceledException):
        j.cancel()


async def test_init():
    set_now(2001, 1, 1, 12, 0, 0)

    s = AsyncScheduler()
    j = OneTimeJob(s, SyncExecutor(lambda: 1 / 0))

    j._schedule_first_run(None)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 0))

    j._schedule_first_run(3)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 3))

    j.cancel()


async def test_next_run():
    set_now(2001, 1, 1, 12, 0, 0)

    s = AsyncScheduler()
    j = OneTimeJob(s, SyncExecutor(lambda: 1 / 0))

    j._schedule_first_run(None)

    assert j.remaining() is not None
    assert j._parent is not None
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 0))

    j._schedule_next_run()
    assert j._parent is None
    assert j.remaining() is None


async def test_func_remaining():
    set_now(2001, 1, 1, 12, 0, 0)

    s = AsyncScheduler()
    j = OneTimeJob(s, SyncExecutor(lambda: 1 / 0))

    j._schedule_first_run(None)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 0))
    assert j.remaining() == timedelta()

    j._schedule_first_run(3)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 3))
    assert j.remaining() == timedelta(seconds=3)

    j._schedule_first_run(7200)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 14, 0, 0))
    assert j.remaining() == timedelta(hours=2)

    j.cancel()

    assert j.remaining() is None
