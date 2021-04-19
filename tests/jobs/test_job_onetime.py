import asyncio
from datetime import datetime

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.errors import JobAlreadyCanceledException, OneTimeJobCanNotBeSkipped
from eascheduler.jobs.job_one_time import OneTimeJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, utc_ts
from tests.helper import mocked_executor, set_now


def test_exception():
    s = AsyncScheduler()
    j = OneTimeJob(s, lambda x: x)
    j._next_base = utc_ts(2001, 1, 1, 12)

    with pytest.raises(OneTimeJobCanNotBeSkipped):
        j.boundary_func(lambda x: SKIP_EXECUTION)


@pytest.mark.asyncio
async def test_remove():

    s = AsyncScheduler()
    e = mocked_executor()
    j = OneTimeJob(s, e)
    set_now(2001, 1, 1, 12, 0, 0)
    j._next_base = utc_ts(2001, 1, 1, 12, microsecond=100_000)
    s.add_job(j)
    j._update_run_time()

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
    j = OneTimeJob(s, lambda x: x)

    j._initialize_base_time(None)
    j._update_run_time()

    cmp_local(j._next_base, datetime(2001, 1, 1, 12, 0, 0, 1))
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 0))

    j._initialize_base_time(3)
    j._update_run_time()
    cmp_local(j._next_base, datetime(2001, 1, 1, 12, 0, 3))
    cmp_local(j._next_run,  datetime(2001, 1, 1, 12, 0, 3))

    j.cancel()
