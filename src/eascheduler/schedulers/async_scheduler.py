from __future__ import annotations

import asyncio
from bisect import insort
from collections import deque
from time import monotonic
from typing import TYPE_CHECKING, Final

from typing_extensions import override

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

    def __repr__(self):
        next_run = f'{self.timer.when() - self._loop.time():.3f}s' if self.timer is not None else 'None'
        return f'<{self.__class__.__name__:s} jobs={len(self.jobs):d} next_run={next_run}>'

    def run_jobs(self) -> None:
        self.timer = None
        jobs = self.jobs

        try:
            while jobs:
                job = jobs[0]
                if job.next_time > monotonic():
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
            self.timer = self._loop.call_later(job.next_time - monotonic(), self.run_jobs)

    @override
    def add_job(self, job: JobBase):
        insort(self.jobs, job)
        if job is self.jobs[0]:
            self._set_timer(job)
        return self

    @override
    def remove_job(self, job: JobBase):
        if not (jobs := self.jobs):
            self._set_timer(None)
            return None

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
    def update_job(self, job: JobBase):
        try:  # noqa: SIM105
            self.jobs.remove(job)
        except ValueError:
            pass

        if job.status is STATUS_RUNNING:
            insort(self.jobs, job)
        if job is self.jobs[0]:
            self._set_timer(job)
        return self
