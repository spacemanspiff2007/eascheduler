from whenever import Instant

from eascheduler.executor import SyncExecutor
from eascheduler.job_stores import InMemoryStore
from eascheduler.jobs import OneTimeJob
from eascheduler.schedulers.async_scheduler import AsyncScheduler


async def test_in_memory() -> None:
    job_id = 'test'
    j = OneTimeJob(SyncExecutor(lambda: None), Instant.now(), job_id=job_id)
    j.link_scheduler(AsyncScheduler(enabled=False))

    m = InMemoryStore()
    assert len(m) == 0
    assert not m

    m.add_job(j)

    assert job_id in m
    assert m[job_id] is j
    assert m.get(job_id) is j
    assert len(m) == 1
    assert m

    j.execute()

    assert job_id not in m
    assert m.get(job_id) is None
    assert len(m) == 0
    assert not m
