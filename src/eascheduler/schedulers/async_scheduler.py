from __future__ import annotations

import asyncio
from bisect import insort
from collections import deque
from time import monotonic
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from eascheduler.errors.handler import process_exception
from eascheduler.jobs.base import STATUS_FINISHED, STATUS_RUNNING
from eascheduler.schedulers.base import SchedulerBase, SchedulerEvents


if TYPE_CHECKING:

    from eascheduler.jobs.base import JobBase


class AsyncScheduler(SchedulerBase):
    __slots__ = ('_loop', 'timer', 'event_handler', 'jobs')

    def __init__(self, event_loop: asyncio.AbstractEventLoop | None = None):
        self._loop: Final = event_loop if event_loop is not None else asyncio.get_running_loop()

        self.timer: asyncio.TimerHandle | None = None
        self.event_handler: SchedulerEvents | None = None
        self.jobs: Final[deque[JobBase]] = deque()

    def set_event_handler(self, view: SchedulerEvents):
        if self.event_handler is not None:
            raise ValueError()
        self.event_handler = view

    def timer_cancel(self):
        if (timer := self.timer) is not None:
            self.timer = None
            timer.cancel()

    def timer_set(self, secs: float | None):
        if (timer := self.timer) is not None:
            timer.cancel()
        self.timer = self._loop.call_later(secs, self.run_jobs) if secs is not None else None

    def timer_update(self):
        self.timer_set(None if not self.jobs else self.jobs[0].next_time - monotonic())

    def run_jobs(self):
        self.timer = None

        jobs = self.jobs
        event_handler = self.event_handler

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

                if job.status is STATUS_RUNNING:
                    insort(jobs, job)
                    if event_handler is not None:
                        event_handler.on_job_executed(job)
                elif job.status == STATUS_FINISHED:
                    if event_handler is not None:
                        event_handler.on_job_finished(job)

        except Exception as e:
            process_exception(e)

        if jobs:
            self.timer_set(monotonic() - jobs[0].next_time)

    @override
    def add_job(self, job: JobBase):
        insort(self.jobs, job)
        self.timer_update()

    @override
    def remove_job(self, job: JobBase):
        self.jobs.remove(job)
        self.timer_update()

    @override
    def update_job(self, job: JobBase):
        try:  # noqa: SIM105
            self.jobs.remove(job)
        except IndexError:
            pass

        if job.status is STATUS_RUNNING:
            insort(self.jobs, job)
        self.timer_update()
