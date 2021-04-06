import asyncio
import time

import pytest

from eascheduler.jobs import CountdownJob
from eascheduler.schedulers import AsyncScheduler
from eascheduler.executors import AsyncExecutor


@pytest.mark.asyncio
async def test_expire():
    s = AsyncScheduler()
    calls = []

    async def a_dummy():
        calls.append(time.time())

    j1 = CountdownJob(s, AsyncExecutor(a_dummy))
    j1.expire(0.2)
    s.add_job(j1)
    # check that adding the trigger doesn't execute the job
    await asyncio.sleep(0.25)

    for _ in range(6):
        j1.reset()
        await asyncio.sleep(0.1)

    await asyncio.sleep(0.15)
    assert len(calls) == 1, calls
    j1.reset()

    await asyncio.sleep(0.25)
    assert len(calls) == 2, calls
    assert calls[1] - calls[0] <= 0.3

    s.cancel_all()
