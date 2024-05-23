from asyncio import Task, create_task
from collections import deque
from typing import Coroutine, Final

from typing_extensions import override

from eascheduler.task_managers.base import TaskManagerBase


class SequentialTaskManager(TaskManagerBase):
    __slots__ = ('task', 'coros')

    def __init__(self):
        self.task: Task | None = None
        self.coros: Final[deque[tuple[Coroutine, str]]] = deque()

    def __repr__(self):
        return f'<{self.__class__.__name__:s} running={self.task is not None} coros={len(self.coros):d}>'

    def _task_done(self, done_task: Task | None):
        self.task = None

        if not (coros := self.coros):
            return None

        coro, name = coros.popleft()
        task = create_task(coro, name=name)
        self.task = task
        task.add_done_callback(self._task_done)
        return task

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        self.coros.append((coro, name))
        if self.task is not None:
            return None

        return self._task_done(None)
