from datetime import datetime
from functools import partial

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.jobs import ReoccurringJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import set_now
from tests.helper import utc_ts


@pytest.mark.asyncio
async def test_remove():

    s = AsyncScheduler()
    j = ReoccurringJob(s, lambda x: x)
    j._next_base = utc_ts(2001, 1, 1, 12, microsecond=0)

    now = partial(set_now, 2001, 1, 1, microsecond=1)
    now(1, microsecond=0)

    s.add_job(j)
    j.interval(5)

    now(11)
    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12)

    now(12)
    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0, 5)
    now(12, 0, 5)

    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0, 10)

    s.cancel_all()


@pytest.mark.asyncio
async def test_skip():

    s = AsyncScheduler()
    j = ReoccurringJob(s, lambda x: x)
    j._next_base = utc_ts(2001, 1, 1, 12, microsecond=0)

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
    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12)

    now(12)
    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0, 5)
    now(12, 0, 5)

    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0, 15)
    now(12, 0, 15)

    j._update_base_time()
    assert j.get_next_run() == datetime(2001, 1, 1, 12, 0, 20)

    s.cancel_all()
