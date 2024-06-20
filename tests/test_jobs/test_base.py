from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import JobBase


async def test_cmp():
    a = JobBase(SyncExecutor(lambda: 1/0))
    b = JobBase(SyncExecutor(lambda: 1/0))

    a.loop_time = 1
    b.loop_time = None
    assert a < b

    a.loop_time = None
    b.loop_time = 1
    assert not a < b

    a.loop_time = 1
    b.loop_time = 2
    assert a < b
