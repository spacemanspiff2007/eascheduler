from asyncio import AbstractEventLoop, create_task, run_coroutine_threadsafe

from eascheduler.errors.handler import process_exception


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
    async def _execute(self):
        try:
            await self._func(*self._args, **self._kwargs)
        except Exception as e:
            process_exception(e)

    def execute(self):
        create_task(self._execute())


class AsyncThreadSafeExecutor(AsyncExecutor):
    #: Running event loop
    LOOP: AbstractEventLoop

    def execute(self):
        run_coroutine_threadsafe(self._execute(), AsyncThreadSafeExecutor.LOOP)
