from __future__ import annotations

from bisect import insort
from collections import deque
from time import monotonic
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from eascheduler.errors.handler import process_exception
from eascheduler.schedulers.base import SchedulerBase


if TYPE_CHECKING:
    import asyncio

    from eascheduler.job_stores.base import JobStoreBase
    from eascheduler.jobs.base import JobBase


class AsyncScheduler(SchedulerBase):
    __slots__ = ('event_loop', 'timer', 'view', 'jobs')

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.event_loop: Final = event_loop

        self.timer: asyncio.TimerHandle | None = None
        self.view: JobStoreBase | None = None
        self.jobs: deque[JobBase] = deque()

    def set_view(self, view: JobStoreBase):
        if self.view is not None:
            raise ValueError()
        self.view = view

    def timer_cancel(self):
        if (timer := self.timer) is not None:
            self.timer = None
            timer.cancel()

    def timer_set(self, secs: float | None):
        if (timer := self.timer) is not None:
            timer.cancel()
        self.timer = self.event_loop.call_later(secs, self.run_jobs) if secs is not None else None

    def timer_update(self):
        self.timer_set(None if not self.jobs else self.jobs[0])

    def run_jobs(self):
        self.timer = None

        jobs = self.jobs
        view = self.view

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

                if job.status == 'running':
                    insort(jobs, job)
                    view.on_job_executed(job)
                elif job.status == 'finished':
                    jobs.remove(job)
                    view.on_job_finished(job)

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

        if job.status == 'running':
            insort(self.jobs, job)
        self.timer_update()
