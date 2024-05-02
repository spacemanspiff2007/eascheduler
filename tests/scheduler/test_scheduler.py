from collections import deque

from eascheduler.old_jobs.job_base import ScheduledJobBase
from eascheduler.old_schedulers import AsyncScheduler


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


async def test_pause_resume():
    async def a_dummy():
        pass

    s = AsyncScheduler()
    s.pause()

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
    assert s.worker_paused
    assert s.worker is None

    s.resume()
    assert s.worker is not None
    assert not s.worker_paused

    s.pause()
    assert s.worker is None
    assert s.worker_paused

    s.cancel_all()

    # without jobs we skip starting the worker
    s.resume()
    assert s.worker is None
    assert not s.worker_paused
