
from asyncio import Task, create_task
from typing import Final, Literal

from typing_extensions import override

from eascheduler.task_manager.base import TaskManagerBase


class ParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks', )

    def __init__(self):
        self.tasks: Final[set[Task]] = set()

    def __repr__(self):
        ct = len(self.tasks)
        return f'<{self.__class__.__name__:s} {ct:d} Task{"" if ct == 1 else "s"}>'

    @override
    def create_task(self, coro, *, name: str | None = None):
        task = create_task(coro, name=name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)


class LimitingParallelTaskManager(TaskManagerBase):
    __slots__ = ('tasks', 'parallel', 'parallel_action')

    def __init__(self, parallel: int, action: Literal['skip', 'cancel_first', 'cancel_last'] = 'skip'):
        super().__init__()
        if parallel < 1:
            raise ValueError()

        self.tasks: Final[list[Task]] = []
        self.parallel: Final = parallel
        self.action: Final = action

    def __repr__(self):
        ct = len(self.tasks)
        return (f'<{self.__class__.__name__:s} '
                f'{ct:d}/{self.parallel:d} Task{"" if ct == 1 else "s"} action: {self.action:s}>')

    def _remove_task(self, task: Task):
        try:  # noqa: SIM105
            self.tasks.remove(task)
        except ValueError:
            pass

    @override
    def create_task(self, coro, *, name: str | None = None):
        if len(self.tasks) > self.parallel:
            if (action := self.action) == 'skip':
                return None

            if action == 'cancel_first':
                self.tasks.pop(0).cancel()
            elif action == 'cancel_last':
                self.tasks.pop(-1).cancel()
            else:
                raise ValueError()

        task = create_task(coro, name=name)
        self.tasks.append(task)
        task.add_done_callback(self._remove_task)
