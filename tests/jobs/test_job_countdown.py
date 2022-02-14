import asyncio
import time
from datetime import datetime

from eascheduler.const import FAR_FUTURE
from eascheduler.executors import AsyncExecutor
from eascheduler.jobs import CountdownJob
from eascheduler.schedulers import AsyncScheduler
from tests.helper import cmp_local, set_now


async def test_expire():
    s = AsyncScheduler()
    calls = []

    async def a_dummy():
        calls.append(time.time())

    j1 = CountdownJob(s, AsyncExecutor(a_dummy))
    j1.countdown(0.2)
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


async def test_stop(async_scheduler: AsyncScheduler):
    set_now(2001, 1, 1, 12, 0, 0)

    calls = []

    async def a_dummy():
        calls.append(time.time())

    j1 = CountdownJob(async_scheduler, AsyncExecutor(a_dummy))
    j1.countdown(120)
    async_scheduler.add_job(j1)

    j1.reset()
    cmp_local(j1._next_run, datetime(2001, 1, 1, 12, 2, 0))

    j1.stop()
    assert j1._next_run == FAR_FUTURE

    j1.reset()
    cmp_local(j1._next_run, datetime(2001, 1, 1, 12, 2, 0))

    # Assert that the callback really gets called
    set_now(2001, 1, 1, 12, 2, 0)
    await asyncio.sleep(0.01)

    assert len(calls) == 1, calls
