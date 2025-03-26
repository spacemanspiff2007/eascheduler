import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from eascheduler.task_managers import (
    LimitingSequentialTaskManager,
    SequentialDeduplicatingTaskManager,
    SequentialTaskManager,
    TaskManagerBase,
)
from eascheduler.task_managers.sequential import HINT_SEQUENTIAL_TASK_POLICY
from tests.helper import assert_literal_values_in_enum


T = TypeVar('T', bound=TaskManagerBase)


def create_tasks(manager: T, arg_func: Callable[[int], Any] | None = None) -> tuple[T, list]:
    res = []

    count = 10

    async def test(value) -> None:
        await asyncio.sleep((count - value) * 0.005)
        res.append(value)

    for i in range(count):
        if arg_func is None:
            manager.create_task(test(i))
        else:
            manager.create_task(test(i), arg_func(i))

    return manager, res


async def await_tasks(m: SequentialTaskManager | SequentialDeduplicatingTaskManager) -> None:
    await asyncio.sleep(0.01)
    while m.task:
        await asyncio.sleep(0.01)


async def test_sequential() -> None:
    t, res = create_tasks(SequentialTaskManager())

    await await_tasks(t)

    assert res == list(range(10))


async def test_repr() -> None:
    m = SequentialTaskManager()
    assert repr(m) == '<SequentialTaskManager running=False queue=0>'

    async def tmp() -> None:
        await asyncio.sleep(0.01)

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True queue=0>'

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True queue=1>'

    await await_tasks(m)


async def test_limiting_repr() -> None:
    m = LimitingSequentialTaskManager(2)
    assert repr(m) == '<LimitingSequentialTaskManager running=False coros=0 max_queue=2 action=skip>'

    async def tmp() -> None:
        await asyncio.sleep(0.01)

    m.create_task(tmp())
    assert repr(m) == '<LimitingSequentialTaskManager running=True coros=0 max_queue=2 action=skip>'

    m.create_task(tmp())
    assert repr(m) == '<LimitingSequentialTaskManager running=True coros=1 max_queue=2 action=skip>'

    await await_tasks(m)


async def test_limiting_skip() -> None:
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip'))

    await await_tasks(t)

    assert res == [0, 1, 2, 3]


async def test_limiting_skip_first() -> None:
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip_first'))

    await await_tasks(t)

    assert res == [0, 7, 8, 9]


async def test_limiting_skip_last() -> None:
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip_last'))

    await await_tasks(t)

    assert res == [0, 1, 2, 9]


async def test_deduplicating_repr() -> None:
    m = SequentialDeduplicatingTaskManager()
    assert repr(m) == '<SequentialDeduplicatingTaskManager running=False queue=0>'

    async def tmp() -> None:
        await asyncio.sleep(0.01)

    m.create_task(tmp(), 1)
    assert repr(m) == '<SequentialDeduplicatingTaskManager running=True queue=0>'

    for _ in range(10):
        m.create_task(tmp(), 1)
        assert repr(m) == '<SequentialDeduplicatingTaskManager running=True queue=1>'

    await await_tasks(m)


async def test_deduplicating_skip() -> None:
    d = dict.fromkeys(range(10), 1)
    d[2] = 2
    d[3] = 3

    t, res = create_tasks(SequentialDeduplicatingTaskManager(), d.get)

    await await_tasks(t)

    assert res == [0, 2, 3, 9]


def test_type_hints() -> None:
    assert_literal_values_in_enum(HINT_SEQUENTIAL_TASK_POLICY)
