from __future__ import annotations

import asyncio
from bisect import insort
from collections import deque
from typing import TYPE_CHECKING, Final

from typing_extensions import Self, override
from whenever import Instant

from eascheduler.errors.errors import JobExecutionTimeIsNotSetError
from eascheduler.errors.handler import process_exception
from eascheduler.jobs.base import STATUS_RUNNING
from eascheduler.schedulers.base import SchedulerBase


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class AsyncScheduler(SchedulerBase):
    __slots__ = ('_loop', 'timer', 'jobs', '_enabled')

    def __init__(self, event_loop: asyncio.AbstractEventLoop | None = None, *, enabled: bool = True) -> None:
        self._loop: Final = event_loop if event_loop is not None else asyncio.get_running_loop()
        self._enabled: bool = enabled
        self.timer: asyncio.TimerHandle | None = None
        self.jobs: Final[deque[JobBase]] = deque()

    def __repr__(self) -> str:
        next_run = f'{self.timer.when() - self._loop.time():.3f}s' if self.timer is not None else 'None'
        enabled = '' if self._enabled else f' enabled={self._enabled}'
        return f'<{self.__class__.__name__:s}{enabled:s} jobs={len(self.jobs):d} next_run={next_run}>'

    def set_enabled(self, enabled: bool) -> Self:  # noqa: FBT001
        if enabled == self._enabled:
            return self

        self._enabled = enabled
        self._set_timer()
        return self

    def run_jobs(self) -> None:
        self.timer = None
        jobs = self.jobs

        try:
            while jobs:
                job = jobs[0]
                if (next_run := job.next_run) is None:
                    raise JobExecutionTimeIsNotSetError()  # noqa: TRY301
                if next_run > Instant.now():
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
            self._set_timer()

    def _set_timer(self) -> None:
        if (timer := self.timer) is not None:
            self.timer = None
            timer.cancel()

        if not (jobs := self.jobs) or not self._enabled:
            return None

        if (next_run := jobs[0].next_run) is None:
            raise JobExecutionTimeIsNotSetError()

        diff = (next_run - Instant.now()).in_seconds()
        if diff <= 0:
            self.run_jobs()
        else:
            self.timer = self._loop.call_at(self._loop.time() + diff, self.run_jobs)

    @override
    def add_job(self, job: JobBase) -> Self:
        if job.status is STATUS_RUNNING:
            insort(self.jobs, job)
            if job is self.jobs[0]:
                self._set_timer()
        return self

    @override
    def remove_job(self, job: JobBase) -> Self:
        if not (jobs := self.jobs):
            self._set_timer()
            return self

        is_first = job is self.jobs[0]
        try:  # noqa: SIM105
            jobs.remove(job)
        except ValueError:
            pass

        if not jobs:
            self._set_timer()
            return self

        if is_first:
            self._set_timer()
        return self

    @override
    def update_job(self, job: JobBase) -> Self:
        self.remove_job(job)
        self.add_job(job)
        return self

    @override
    def remove_all(self) -> Self:
        for job in tuple(reversed(self.jobs)):
            job.job_finish()
        return self
