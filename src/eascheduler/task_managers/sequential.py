from asyncio import Task, create_task
from collections import deque
from enum import Enum
from typing import Coroutine, Final

from typing_extensions import override

from eascheduler.task_managers.base import TaskManagerBase


class SequentialTaskPolicy(str, Enum):
    SKIP = 'skip'
    SKIP_FIRST = 'skip_first'
    SKIP_LAST = 'skip_last'


POLICY_SKIP = SequentialTaskPolicy.SKIP
POLICY_SKIP_FIRST = SequentialTaskPolicy.SKIP_FIRST
POLICY_SKIP_LAST = SequentialTaskPolicy.SKIP_LAST


class SequentialTaskManager(TaskManagerBase):
    __slots__ = ('task', 'queue')

    def __init__(self):
        self.task: Task | None = None
        self.queue: Final[deque[tuple[Coroutine, str]]] = deque()

    def __repr__(self):
        return f'<{self.__class__.__name__:s} running={self.task is not None} queue={len(self.queue):d}>'

    def _task_done(self, done_task: Task | None) -> Task | None:
        if done_task is self.task:
            self.task = None

        if not (queue := self.queue):
            return None

        coro, name = queue.popleft()
        task = create_task(coro, name=name)
        self.task = task
        task.add_done_callback(self._task_done)
        return task

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        self.queue.append((coro, name))
        if self.task is not None:
            return None

        return self._task_done(None)


class LimitingSequentialTaskManager(SequentialTaskManager):
    __slots__ = ('max_queue', 'action')

    def __init__(self, max_queue: int, action: SequentialTaskPolicy | str = POLICY_SKIP):
        super().__init__()
        if not isinstance(max_queue, int) or max_queue < 1:
            raise ValueError()

        self.max_queue: Final = max_queue
        self.action: Final[SequentialTaskPolicy] = \
            SequentialTaskPolicy(action) if not isinstance(action, SequentialTaskPolicy) else action

    def __repr__(self):
        return (
            f'<{self.__class__.__name__:s} running={self.task is not None} coros={len(self.queue):d} '
            f'max_queue={self.max_queue:d} action={self.action.value}>'
        )

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:

        if len(queue := self.queue) >= self.max_queue:
            if (action := self.action) is POLICY_SKIP:
                return None

            if action is POLICY_SKIP_FIRST:
                queue.popleft()
            elif action is POLICY_SKIP_LAST:
                queue.pop()
            else:
                raise ValueError()

        queue.append((coro, name))
        if self.task is not None:
            return None

        return self._task_done(None)
