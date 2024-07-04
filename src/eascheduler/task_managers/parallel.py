from asyncio import Task, create_task
from collections import deque
from collections.abc import Coroutine
from enum import Enum
from typing import Final

from typing_extensions import override

from eascheduler.task_managers.base import TaskManagerBase


class ParallelTaskPolicy(str, Enum):
    SKIP = 'skip'
    CANCEL_FIRST = 'cancel_first'
    CANCEL_LAST = 'cancel_last'


POLICY_SKIP = ParallelTaskPolicy.SKIP
POLICY_CANCEL_FIRST = ParallelTaskPolicy.CANCEL_FIRST
POLICY_CANCEL_LAST = ParallelTaskPolicy.CANCEL_LAST


class ParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks',)

    def __init__(self) -> None:
        self.tasks: Final[set[Task]] = set()

    def __repr__(self) -> str:
        ct = len(self.tasks)
        return f'<{self.__class__.__name__:s} {ct:d} Task{"" if ct == 1 else "s"}>'

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        task = create_task(coro, name=name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task


class LimitingParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks', 'parallel', 'action')

    def __init__(self, parallel: int, action: ParallelTaskPolicy | str = POLICY_SKIP):
        super().__init__()
        if not isinstance(parallel, int) or parallel < 1:
            raise ValueError()

        self.tasks: Final[deque[Task]] = deque()
        self.parallel: Final = parallel
        self.action: Final[ParallelTaskPolicy] = \
            ParallelTaskPolicy(action) if not isinstance(action, ParallelTaskPolicy) else action

    def __repr__(self) -> str:
        ct = len(self.tasks)
        return (f'<{self.__class__.__name__:s} '
                f'{ct:d}/{self.parallel:d} Task{"" if ct == 1 else "s"} action={self.action.value:s}>')

    def _remove_task(self, task: Task) -> None:
        try:  # noqa: SIM105
            self.tasks.remove(task)
        except ValueError:
            pass

    @override
    def create_task(self, coro, *, name: str | None = None) -> Task | None:
        if len(self.tasks) >= self.parallel:
            if (action := self.action) is POLICY_SKIP:
                coro.close()
                return None

            if action is POLICY_CANCEL_FIRST:
                self.tasks.popleft().cancel()
            elif action is POLICY_CANCEL_LAST:
                self.tasks.pop().cancel()
            else:
                raise ValueError()

        task = create_task(coro, name=name)
        self.tasks.append(task)
        task.add_done_callback(self._remove_task)
        return task
