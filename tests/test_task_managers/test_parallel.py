import asyncio
from typing import TypeVar

from eascheduler.task_managers import LimitingParallelTaskManager, ParallelTaskManager, TaskManagerBase


T = TypeVar('T', bound=TaskManagerBase)


def create_tasks(manager: T) -> tuple[T, set]:
    res = set()

    async def test(value):
        await asyncio.sleep(0.05)
        res.add(value)

    for i in range(10):
        manager.create_task(test(i))

    return manager, res


async def test_parallel():
    t, res = create_tasks(ParallelTaskManager())

    assert len(t.tasks) == 10
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == set(range(10))


async def test_parallel_limiting():
    t, res = create_tasks(LimitingParallelTaskManager(3))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == set(range(3))


async def test_parallel_cancel_first():
    t, res = create_tasks(LimitingParallelTaskManager(3, 'cancel_first'))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == {7, 8, 9}


async def test_parallel_cancel_last():
    t, res = create_tasks(LimitingParallelTaskManager(3, 'cancel_last'))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == {0, 1, 9}
