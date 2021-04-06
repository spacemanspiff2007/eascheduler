import asyncio

import pytest

from eascheduler.const import SKIP_EXECUTION
from eascheduler.errors import OneTimeJobCanNotBeSkipped, JobAlreadyCanceledException
from eascheduler.jobs.job_one_time import OneTimeJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import mocked_executor, set_now
from tests.helper import utc_ts


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
