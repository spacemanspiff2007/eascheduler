import asyncio
from asyncio import create_task, Future
from bisect import insort
from collections import deque
from typing import Deque, Optional, Set

from pendulum import now as get_now
from pendulum import UTC

from eascheduler.const import FAR_FUTURE
from eascheduler.errors.handler import process_exception
from eascheduler.jobs.job_base import ScheduledJobBase


class AsyncScheduler:
    def __init__(self):
        self.jobs: Deque[ScheduledJobBase] = deque()
        self.job_objs: Set[ScheduledJobBase] = set()

        self.worker: Optional[Future] = None
        self.worker_paused: bool = False

    def pause(self):
        assert not self.worker_paused

        self.worker_paused = True
        if self.worker is not None:
            self.worker.cancel()
            self.worker = None

    def resume(self):
        assert self.worker_paused

        if self.jobs:
            self.worker = create_task(self._run_next())
        self.worker_paused = False

    def add_job(self, job: ScheduledJobBase):
        # cancel task if the new job is earlier than the next one or if it is the next one
        first_job = self.jobs and (job is self.jobs[0] or job._next_run <= self.jobs[0]._next_run)
        if first_job and self.worker is not None:
            self.worker.cancel()
            self.worker = None

        if job not in self.job_objs:
            insort(self.jobs, job)
            self.job_objs.add(job)
        else:
            self.jobs.remove(job)
            insort(self.jobs, job)

        if self.worker is None and not self.worker_paused:
            self.worker = create_task(self._run_next())

    def remove_job(self, job: ScheduledJobBase):
        if self.jobs and job is self.jobs[0]:
            # if it's the first job we have to cancel the task
            if self.worker is not None:
                self.worker.cancel()
                self.worker = None

            self.jobs.popleft()
            self.job_objs.remove(job)

            if self.jobs and not self.worker_paused:
                self.worker = create_task(self._run_next())
        else:
            self.jobs.remove(job)
            self.job_objs.remove(job)

    def cancel_all(self):
        if self.worker is not None:
            self.worker.cancel()
            self.worker = None

        while self.jobs:
            job = self.jobs.popleft()
            self.job_objs.remove(job)
            job._parent = None

    async def _run_next(self):
        try:
            while self.jobs:
                job = self.jobs[0]

                # Don't schedule these jobs
                if job._next_run >= FAR_FUTURE:
                    break

                now = get_now(UTC).timestamp()
                diff = job._next_run - now

                while diff > 0:
                    await asyncio.sleep(diff)
                    now = get_now(UTC).timestamp()
                    diff = job._next_run - now

                old_job = job
                job = self.jobs.popleft()
                self.job_objs.remove(job)

                assert old_job is job, f'Job changed unexpectedly\n{old_job}\n{job}'

                try:
                    job._execute()
                except Exception as e:
                    process_exception(e)

        except Exception as e:

            # callback for normal exceptions
            process_exception(e)

        # Never ever put this in a "finally" block!
        # We will get a race condition if we cancel the task!
        self.worker = None
