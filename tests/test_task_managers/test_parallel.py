import asyncio
from typing import TypeVar

from eascheduler.task_managers import LimitingParallelTaskManager, ParallelTaskManager, TaskManagerBase
from eascheduler.task_managers.parallel import HINT_PARALLEL_TASK_POLICY
from tests.helper import assert_literal_values_in_enum


T = TypeVar('T', bound=TaskManagerBase)


def create_tasks(manager: T) -> tuple[T, set]:
    res = set()

    async def test(value) -> None:
        await asyncio.sleep(0.05)
        res.add(value)

    for i in range(10):
        manager.create_task(test(i))

    return manager, res


async def test_repr() -> None:
    m = ParallelTaskManager()

    async def tmp() -> None:
        await asyncio.sleep(0)

    assert repr(m) == '<ParallelTaskManager 0 Tasks>'

    m.create_task(tmp())
    assert repr(m) == '<ParallelTaskManager 1 Task>'

    m.create_task(tmp())
    assert repr(m) == '<ParallelTaskManager 2 Tasks>'

    await asyncio.sleep(0.01)


async def test_parallel() -> None:
    t, res = create_tasks(ParallelTaskManager())

    assert len(t.tasks) == 10
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == set(range(10))


async def test_repr_limiting() -> None:
    m = LimitingParallelTaskManager(3)

    async def tmp() -> None:
        await asyncio.sleep(0)

    assert repr(m) == '<LimitingParallelTaskManager 0/3 Tasks action=skip>'

    m.create_task(tmp())
    assert repr(m) == '<LimitingParallelTaskManager 1/3 Task action=skip>'

    m.create_task(tmp())
    assert repr(m) == '<LimitingParallelTaskManager 2/3 Tasks action=skip>'

    await asyncio.sleep(0.01)


async def test_parallel_limiting() -> None:
    t, res = create_tasks(LimitingParallelTaskManager(3))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == set(range(3))


async def test_parallel_cancel_first() -> None:
    t, res = create_tasks(LimitingParallelTaskManager(3, 'cancel_first'))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == {7, 8, 9}


async def test_parallel_cancel_last() -> None:
    t, res = create_tasks(LimitingParallelTaskManager(3, 'cancel_last'))

    assert len(t.tasks) == 3
    await asyncio.sleep(0.1)
    assert len(t.tasks) == 0
    assert res == {0, 1, 9}


def test_type_hints() -> None:
    assert_literal_values_in_enum(HINT_PARALLEL_TASK_POLICY)
