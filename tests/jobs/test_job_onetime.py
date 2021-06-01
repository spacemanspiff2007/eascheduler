import asyncio
from datetime import datetime

import pytest

from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.executors import SyncExecutor
from eascheduler.jobs.job_one_time import OneTimeJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, mocked_executor, set_now, utc_ts


@pytest.mark.asyncio
async def test_remove():

    s = AsyncScheduler()
    e = mocked_executor()
    j = OneTimeJob(s, e)
    set_now(2001, 1, 1, 12, 0, 0)
    j._next_run_base = utc_ts(2001, 1, 1, 12, microsecond=100_000)
    j._set_next_run(j._next_run_base)

    e.mock.assert_not_called()

    await asyncio.sleep(0.05)
    set_now(2001, 1, 1, 12, microsecond=100_001)
    await asyncio.sleep(0.1)

    e.mock.assert_called_once()

    assert j not in s.jobs
    assert j not in s.job_objs
    assert j._parent is None

    with pytest.raises(JobAlreadyCanceledException):
        j.cancel()


@pytest.mark.asyncio
async def test_init():
    set_now(2001, 1, 1, 12, 0, 0)

    s = AsyncScheduler()
    j = OneTimeJob(s, SyncExecutor(lambda: 1 / 0))

    j._schedule_first_run(None)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 0))

    j._schedule_first_run(3)
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 3))

    j.cancel()
