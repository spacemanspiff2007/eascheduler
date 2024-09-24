from whenever import Instant

from eascheduler.executor.base import SyncExecutor
from eascheduler.jobs.base import JobBase
from tests.helper import AlwaysError


async def test_cmp() -> None:
    a = JobBase(SyncExecutor(AlwaysError()))
    b = JobBase(SyncExecutor(AlwaysError()))

    a.next_run = Instant.from_utc(2001, 1, 1)
    b.next_run = None
    assert a < b

    a.next_run = None
    b.next_run = Instant.from_utc(2001, 1, 1)
    assert a > b

    a.next_run = Instant.from_utc(2001, 1, 1)
    b.next_run = Instant.from_utc(2001, 1, 1, nanosecond=1)
    assert a < b
