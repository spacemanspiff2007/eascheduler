from asyncio import sleep, get_event_loop
from concurrent.futures import ThreadPoolExecutor

import pytest

from eascheduler.executors import SyncExecutor
from eascheduler.scheduler_view import SchedulerView
from eascheduler.schedulers import ThreadSafeAsyncScheduler


@pytest.mark.asyncio
async def test_sort():
    async def a_dummy():
        pass

    executor = ThreadPoolExecutor(max_workers=5)

    s = ThreadSafeAsyncScheduler()
    s.LOOP = get_event_loop()

    view = SchedulerView(s, SyncExecutor)

    def create_job():
        view.every(None, 1, lambda: 0)

    objs = []
    for _ in range(20):
        objs.append(executor.submit(create_job))

    while not any(map(lambda x: x.done(), objs)):
        await sleep(0.1)

    for obj in objs:
        obj.result()
        obj.exception()

    await sleep(0.1)

    s.cancel_all()
