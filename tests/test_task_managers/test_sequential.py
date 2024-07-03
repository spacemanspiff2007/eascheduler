import asyncio
from typing import Any, Callable, TypeVar

from eascheduler.task_managers import (
    LimitingSequentialTaskManager,
    SequentialDeduplicatingTaskManager,
    SequentialTaskManager,
    TaskManagerBase,
)


T = TypeVar('T', bound=TaskManagerBase)


TASKS = []


def create_tasks(manager: T, arg_func: Callable[[int], Any] | None = None) -> tuple[T, list]:
    res = []

    count = 10

    async def test(value):
        await asyncio.sleep((count - value) * 0.005)
        res.append(value)

    for i in range(count):
        if arg_func is None:  # noqa: SIM108
            t = manager.create_task(test(i))
        else:
            t = manager.create_task(test(i), arg_func(i))

        if t is not None:
            TASKS.append(t)

    return manager, res


async def await_tasks(m: SequentialTaskManager | SequentialDeduplicatingTaskManager):
    await asyncio.sleep(0.01)

    # wait till queue is empty
    while m.task:
        await asyncio.sleep(0.01)

    # await task objects
    for t in TASKS:
        await t
    TASKS.clear()


async def test_sequential():
    t, res = create_tasks(SequentialTaskManager())

    await await_tasks(t)

    assert res == list(range(10))


async def test_repr():
    m = SequentialTaskManager()
    assert repr(m) == '<SequentialTaskManager running=False queue=0>'

    async def tmp():
        await asyncio.sleep(0.01)

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True queue=0>'

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True queue=1>'

    await await_tasks(m)


async def test_limiting_repr():
    m = LimitingSequentialTaskManager(2)
    assert repr(m) == '<LimitingSequentialTaskManager running=False coros=0 max_queue=2 action=skip>'

    async def tmp():
        await asyncio.sleep(0.01)

    m.create_task(tmp())
    assert repr(m) == '<LimitingSequentialTaskManager running=True coros=0 max_queue=2 action=skip>'

    m.create_task(tmp())
    assert repr(m) == '<LimitingSequentialTaskManager running=True coros=1 max_queue=2 action=skip>'

    await await_tasks(m)


async def test_limiting_skip():
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip'))

    await await_tasks(t)

    assert res == [0, 1, 2, 3]


async def test_limiting_skip_first():
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip_first'))

    await await_tasks(t)

    assert res == [0, 7, 8, 9]


async def test_limiting_skip_last():
    t, res = create_tasks(LimitingSequentialTaskManager(3, 'skip_last'))

    await await_tasks(t)

    assert res == [0, 1, 2, 9]


async def test_deduplicating_repr():
    m = SequentialDeduplicatingTaskManager()
    assert repr(m) == '<SequentialDeduplicatingTaskManager running=False queue=0>'

    async def tmp():
        await asyncio.sleep(0.01)

    m.create_task(tmp(), 1)
    assert repr(m) == '<SequentialDeduplicatingTaskManager running=True queue=0>'

    for _ in range(10):
        m.create_task(tmp(), 1)
        assert repr(m) == '<SequentialDeduplicatingTaskManager running=True queue=1>'

    await await_tasks(m)


async def test_deduplicating_skip():
    d = {k: 1 for k in range(10)}
    d[2] = 2
    d[3] = 3

    t, res = create_tasks(SequentialDeduplicatingTaskManager(), d.get)

    await await_tasks(t)

    assert res == [0, 2, 3, 9]
