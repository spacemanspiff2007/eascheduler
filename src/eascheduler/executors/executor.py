import logging
from asyncio import create_task, run_coroutine_threadsafe, AbstractEventLoop
from typing import Any, Callable

log = logging.getLogger('AsyncScheduler')


def default_exception_handler(e: Exception):
    log.error(str(e))


class ExecutorBase:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def execute(self):
        raise NotImplementedError()


class SyncExecutor(ExecutorBase):
    def execute(self):
        self._func(*self._args, **self._kwargs)


class AsyncExecutor(ExecutorBase):
    #: Function which will be called when an ``Exception`` occurs during the execution of the job
    EXCEPTION_HANDLER: Callable[[Exception], Any] = default_exception_handler

    async def _execute(self):
        try:
            await self._func(*self._args, **self._kwargs)
        except Exception as e:
            default_exception_handler(e)

    def execute(self):
        create_task(self._execute())


class AsyncThreadSafeExecutor(AsyncExecutor):
    #: Running event loop
    LOOP: AbstractEventLoop

    def execute(self):
        run_coroutine_threadsafe(self.execute(), AsyncThreadSafeExecutor.LOOP)
