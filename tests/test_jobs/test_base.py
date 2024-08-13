from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import JobBase
from tests.helper import AlwaysError


async def test_cmp():
    a = JobBase(SyncExecutor(AlwaysError()))
    b = JobBase(SyncExecutor(AlwaysError()))

    a.loop_time = 1
    b.loop_time = None
    assert a < b

    a.loop_time = None
    b.loop_time = 1
    assert not a < b

    a.loop_time = 1
    b.loop_time = 2
    assert a < b
