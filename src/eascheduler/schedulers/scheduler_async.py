import asyncio
from asyncio import Future, CancelledError, create_task
from bisect import insort
from collections import deque
from typing import Deque, Optional, Set

from pendulum import UTC
from pendulum import now as get_now

from eascheduler.const import FAR_FUTURE
from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.errors.handler import process_exception


class AsyncScheduler:
    def __init__(self):
        self.jobs: Deque[ScheduledJobBase] = deque()
        self.job_objs: Set[ScheduledJobBase] = set()

        self.worker: Optional[Future] = None

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

        if self.worker is None:
            self.worker = create_task(self.__run_next())

    def remove_job(self, job: ScheduledJobBase):
        if self.jobs and job is self.jobs[0]:
            # if it's the first job we have to cancel the task
            if self.worker is not None:
                self.worker.cancel()
                self.worker = None

            self.jobs.popleft()
            self.job_objs.remove(job)

            if self.jobs:
                self.worker = create_task(self.__run_next())
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

    async def __run_next(self):
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
                    # If it's a reoccurring job it has this function
                    if hasattr(job, '_update_base_time'):
                        job._update_base_time()
                    else:
                        job._parent = None

                    job._func.execute()
                except Exception as e:
                    process_exception(e)

        except Exception as e:
            # Todo: remove this once we go >= 3.8
            # With python 3.7 this will also catch the CancelledError
            if isinstance(e, CancelledError):
                raise

            # callback for normal exceptions
            process_exception(e)

        # Never ever put this in a finally block!
        # We will get a race condition if we cancel the task!
        self.worker = None
