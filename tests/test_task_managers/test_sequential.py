import asyncio
from typing import TypeVar

from eascheduler.task_managers import SequentialTaskManager, TaskManagerBase


T = TypeVar('T', bound=TaskManagerBase)


def create_tasks(manager: T) -> tuple[T, list]:
    res = []

    count = 10

    async def test(value):
        await asyncio.sleep((count - value) * 0.005)
        res.append(value)

    for i in range(count):
        manager.create_task(test(i))

    return manager, res


async def await_tasks(m: SequentialTaskManager):
    await asyncio.sleep(0.01)
    while m.task:
        await asyncio.sleep(0.01)


async def test_sequential():
    t, res = create_tasks(SequentialTaskManager())

    await await_tasks(t)

    assert res == list(range(10))


async def test_repr():
    m = SequentialTaskManager()
    assert repr(m) == '<SequentialTaskManager running=False coros=0>'

    async def tmp():
        await asyncio.sleep(0.01)

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True coros=0>'

    m.create_task(tmp())
    assert repr(m) == '<SequentialTaskManager running=True coros=1>'

    await await_tasks(m)
