from collections import deque

import pytest

from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler


@pytest.mark.asyncio
async def test_sort():
    async def a_dummy():
        pass

    s = AsyncScheduler()

    def job(time):
        obj = ScheduledJobBase(s, a_dummy)
        obj._next_run = time
        s.add_job(obj)
        return obj

    first = job(1.1)
    third = job(1.3)
    fourth = job(1.4)
    second = job(1.2)

    assert s.jobs == deque((first, second, third, fourth))

    assert s.jobs[0]._next_run == 1.1
    assert s.jobs[1]._next_run == 1.2
    assert s.jobs[2]._next_run == 1.3
    assert s.jobs[3]._next_run == 1.4

    s.remove_job(third)
    assert s.jobs == deque((first, second, fourth))

    s.remove_job(first)
    assert s.jobs == deque((second, fourth))

    s.remove_job(fourth)
    assert s.jobs == deque((second, ))

    s.remove_job(second)
    assert s.jobs == deque()
    assert s.job_objs == set()
