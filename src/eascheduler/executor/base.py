from typing import Any, Awaitable, Callable, Final, override

from eascheduler.errors.handler import process_exception
from eascheduler.task_managers import ParallelTaskManager, TaskManagerBase


class ExecutorBase:
    def execute(self):
        raise NotImplementedError()


# Sync e.g. for testing
class SyncExecutor(ExecutorBase):
    def __init__(self, coro: Callable[..., Any], args: tuple = (), kwargs: dict | None = None):
        self._func: Final = coro
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

    @override
    def execute(self):
        try:
            self._func(*self._args, **self._kwargs)
        except Exception as e:
            process_exception(e)


class AsyncExecutor(ExecutorBase):
    def __init__(self, coro: Callable[..., Awaitable[Any]], args: tuple = (), kwargs: dict | None = None,
                 task_manager: TaskManagerBase | None = None):
        self._func: Final = coro
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

        self.task_manager: Final = task_manager if task_manager is not None else ParallelTaskManager()

    async def _execute(self):
        try:
            await self._func(*self._args, **self._kwargs)
        except Exception as e:
            process_exception(e)

    @override
    def execute(self):
        self.task_manager.create_task(self._execute())
