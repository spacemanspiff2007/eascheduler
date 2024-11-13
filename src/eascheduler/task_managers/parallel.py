from asyncio import Task, create_task
from collections import deque
from collections.abc import Coroutine
from enum import Enum
from typing import Final, Literal, TypeAlias

from typing_extensions import override

from eascheduler.helpers.helpers import to_enum
from eascheduler.task_managers.base import TaskManagerBase


class ParallelTaskPolicy(str, Enum):
    SKIP = 'skip'
    CANCEL_FIRST = 'cancel_first'
    CANCEL_LAST = 'cancel_last'


POLICY_SKIP = ParallelTaskPolicy.SKIP
POLICY_CANCEL_FIRST = ParallelTaskPolicy.CANCEL_FIRST
POLICY_CANCEL_LAST = ParallelTaskPolicy.CANCEL_LAST


HINT_PARALLEL_TASK_POLICY: TypeAlias = ParallelTaskPolicy | Literal['skip', 'cancel_first', 'cancel_last']


class ParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks',)

    def __init__(self) -> None:
        self.tasks: Final[set[Task]] = set()

    def __repr__(self) -> str:
        ct = len(self.tasks)
        return f'<{self.__class__.__name__:s} {ct:d} Task{"" if ct == 1 else "s"}>'

    @override
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        """Create a new task. All tasks will run parallel

        :param coro: Coro
        :param name: Task name
        """
        task = create_task(coro, name=name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task


class LimitingParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks', 'parallel', 'action')

    def __init__(self, parallel: int, action: HINT_PARALLEL_TASK_POLICY = POLICY_SKIP) -> None:
        """

        :param parallel: Maximum parallel tasks
        :param action: What to do when the limit is exceeded
        """
        super().__init__()
        if not isinstance(parallel, int) or parallel < 1:
            raise ValueError()

        self.tasks: Final[deque[Task]] = deque()
        self.parallel: Final = parallel
        self.action: Final[ParallelTaskPolicy] = to_enum(ParallelTaskPolicy, action)

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
    def create_task(self, coro: Coroutine, *, name: str | None = None) -> Task | None:
        """Create a new task. All tasks will run until the max parallel limit is reached.
        Depending on the action, the oldest or the newest the task will be cancelled
        or the to be created task will be skipped.

        :param coro: Coro
        :param name: Task name
        """
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
