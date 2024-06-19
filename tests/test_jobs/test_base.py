from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import JobBase


async def test_cmp():
    a = JobBase(SyncExecutor(lambda: 1/0))
    b = JobBase(SyncExecutor(lambda: 1/0))

    a.next_time = 1
    b.next_time = None
    assert a < b

    a.next_time = None
    b.next_time = 1
    assert not a < b

    a.next_time = 1
    b.next_time = 2
    assert a < b
