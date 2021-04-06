import logging
from asyncio import run_coroutine_threadsafe, AbstractEventLoop

from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler

log = logging.getLogger('AsyncScheduler')


class ThreadSafeAsyncScheduler(AsyncScheduler):
    LOOP: AbstractEventLoop

    async def __add_job(self, job: ScheduledJobBase):
        super().add_job(job)

    def add_job(self, job: ScheduledJobBase):
        coro = run_coroutine_threadsafe(self.__add_job(job), self.LOOP)
        return coro.result()

    async def __remove_job(self, job: ScheduledJobBase):
        super().remove_job(job)

    def remove_job(self, job: ScheduledJobBase):
        coro = run_coroutine_threadsafe(self.__remove_job(job), self.LOOP)
        return coro.result()

    async def __cancel_all(self):
        super().cancel_all()

    def cancel_all(self):
        coro = run_coroutine_threadsafe(self.__cancel_all(), self.LOOP)
        return coro.result()
