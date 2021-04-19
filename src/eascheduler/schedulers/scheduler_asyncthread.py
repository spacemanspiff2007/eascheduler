import logging
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from threading import current_thread
from threading import _MainThread   # type: ignore

from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler

log = logging.getLogger('AsyncScheduler')


class ThreadSafeAsyncScheduler(AsyncScheduler):
    LOOP: AbstractEventLoop

    async def __add_job(self, job: ScheduledJobBase):
        super().add_job(job)

    def add_job(self, job: ScheduledJobBase):
        if not isinstance(current_thread(), _MainThread):
            run_coroutine_threadsafe(self.__add_job(job), self.LOOP).result()
        else:
            super().add_job(job)
        return None

    async def __remove_job(self, job: ScheduledJobBase):
        super().remove_job(job)

    def remove_job(self, job: ScheduledJobBase):
        if not isinstance(current_thread(), _MainThread):
            run_coroutine_threadsafe(self.__remove_job(job), self.LOOP).result()
        else:
            super().remove_job(job)
        return None

    async def __cancel_all(self):
        super().cancel_all()

    def cancel_all(self):
        if not isinstance(current_thread(), _MainThread):
            run_coroutine_threadsafe(self.__cancel_all(), self.LOOP).result()
        else:
            super().cancel_all()
        return None
