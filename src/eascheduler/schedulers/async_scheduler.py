from __future__ import annotations

import asyncio
from bisect import insort
from collections import deque
from typing import TYPE_CHECKING, Final

from typing_extensions import Self, override
from whenever import UTCDateTime

from eascheduler.errors import ScheduledRunInThePastError
from eascheduler.errors.errors import JobExecutionTimeIsNotSetError
from eascheduler.errors.handler import process_exception
from eascheduler.jobs.base import STATUS_RUNNING
from eascheduler.schedulers.base import SchedulerBase


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class AsyncScheduler(SchedulerBase):
    __slots__ = ('_loop', 'timer', 'jobs')

    def __init__(self, event_loop: asyncio.AbstractEventLoop | None = None) -> None:
        self._loop: Final = event_loop if event_loop is not None else asyncio.get_running_loop()
        self.timer: asyncio.TimerHandle | None = None
        self.jobs: Final[deque[JobBase]] = deque()

    def __repr__(self) -> str:
        next_run = f'{self.timer.when() - self._loop.time():.3f}s' if self.timer is not None else 'None'
        return f'<{self.__class__.__name__:s} jobs={len(self.jobs):d} next_run={next_run}>'

    def run_jobs(self) -> None:
        self.timer = None
        jobs = self.jobs
        loop = self._loop

        try:
            while jobs:
                job = jobs[0]
                if (loop_time := job.loop_time) is None:
                    raise JobExecutionTimeIsNotSetError()  # noqa: TRY301
                if loop_time > loop.time():
                    break

                jobs.popleft()

                try:
                    job.execute()
                except Exception as e:
                    process_exception(e)

                # Reschedule job if it's still running
                if job.status is STATUS_RUNNING:
                    self.add_job(job)

        except Exception as e:
            process_exception(e)

        if jobs:
            self._set_timer(jobs[0])

    def _set_timer(self, job: JobBase | None) -> None:
        if (timer := self.timer) is not None:
            timer.cancel()

        if job is None:
            self.timer = None
        else:
            if (loop_time := job.loop_time) is None:
                raise JobExecutionTimeIsNotSetError()
            self.timer = self._loop.call_at(loop_time, self.run_jobs)

    @override
    def set_job_time(self, job: JobBase, next_time: UTCDateTime | None) -> Self:

        if next_time is None:
            job.set_loop_time(None, None)
            return self

        loop_now = self._loop.time()
        loop_next = loop_now + (next_time - UTCDateTime.now()).in_seconds()
        if loop_next < loop_now - 0.1:
            raise ScheduledRunInThePastError()

        job.set_loop_time(loop_next, next_time)
        return self

    @override
    def add_job(self, job: JobBase) -> Self:
        if job.status is STATUS_RUNNING:
            insort(self.jobs, job)
            if job is self.jobs[0]:
                self._set_timer(job)
        return self

    @override
    def remove_job(self, job: JobBase) -> Self:
        if not (jobs := self.jobs):
            self._set_timer(None)
            return self

        is_first = job is self.jobs[0]
        try:  # noqa: SIM105
            jobs.remove(job)
        except ValueError:
            pass

        if not jobs:
            self._set_timer(None)
            return self

        if is_first:
            self._set_timer(jobs[0])
        return self

    @override
    def update_job(self, job: JobBase) -> Self:
        self.remove_job(job)
        self.add_job(job)
        return self
