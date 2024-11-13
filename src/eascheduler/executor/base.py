from collections.abc import Awaitable, Callable, Iterable, Mapping
from typing import Any, Final

from typing_extensions import override

from eascheduler.errors.handler import process_exception
from eascheduler.task_managers import ParallelTaskManager, TaskManagerBase


class ExecutorBase:
    def execute(self) -> None:
        raise NotImplementedError()


# Sync e.g. for testing
class SyncExecutor(ExecutorBase):
    def __init__(self, func: Callable[..., Any], args: Iterable = (), kwargs: Mapping[str, Any] | None = None) -> None:
        self._func: Final = func
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

    @override
    def execute(self) -> None:
        try:
            self._func(*self._args, **self._kwargs)
        except Exception as e:
            process_exception(e)


DEFAULT_TASK_MANAGER: TaskManagerBase = ParallelTaskManager()


class AsyncExecutor(ExecutorBase):
    def __init__(self, coro_func: Callable[..., Awaitable[Any]],
                 args: Iterable = (), kwargs: Mapping[str, Any] | None = None,
                 task_manager: TaskManagerBase | None = None) -> None:
        self._func: Final = coro_func
        self._args: Final = args
        self._kwargs: Final = kwargs if kwargs is not None else {}

        self.task_manager: Final = task_manager if task_manager is not None else DEFAULT_TASK_MANAGER

    async def _execute(self) -> None:
        try:
            await self._func(*self._args, **self._kwargs)
        except Exception as e:
            process_exception(e)

    @override
    def execute(self) -> None:
        self.task_manager.create_task(self._execute())
