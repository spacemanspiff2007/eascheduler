from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import SchedulerBase


if TYPE_CHECKING:
    import asyncio

    from eascheduler.jobs.base import JobBase


class AsyncScheduler(SchedulerBase):
    __slots__ = ('event_loop', 'jobs', 'timer')

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.event_loop: Final = event_loop
        self.jobs: Final[list[JobBase]] = []
        self.timer: asyncio.TimerHandle | None = None

    def timer_cancel(self):
        if (timer := self.timer) is not None:
            self.timer = None
            timer.cancel()

    def timer_set(self, secs: float | None):
        if (timer := self.timer) is not None:
            timer.cancel()
        self.timer = self.event_loop.call_later(secs, self.run_jobs) if secs is not None else None

    def timer_update(self):
        self.timer_set(
            min(((nt for job in self.jobs if (nt := job.next_time)) is not None), default=None)
        )

    def run_jobs(self):
        self.timer = None

        next_time: float | None = None

        remove = []
        for job in self.jobs:
            if (job_time := job.next_time) is None:
                continue

            if monotonic() >= job_time:
                if job.execute() == 'finished':
                    remove.append(job)

            next_time = job_time if next_time is None else min(next_time, job_time)

        if next_time is not None:
            self.timer_set(monotonic() - next_time)

        for job in remove:
            self.jobs.remove(job)

    @override
    def add_job(self, job: JobBase):
        self.jobs.append(job)
        self.timer_update()

    @override
    def remove_job(self, job: JobBase):
        self.jobs.remove(job)
        self.timer_update()

    @override
    def job_changed(self, job: JobBase):
        self.timer_update()
