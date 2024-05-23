from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class SchedulerBase:
    def add_job(self, job: JobBase):
        pass

    def remove_job(self, job: JobBase):
        pass

    def update_job(self, job: JobBase):
        pass


class SchedulerEvents:
    def on_job_finished(self, job: JobBase):
        raise NotImplementedError()

    def on_job_executed(self, job: JobBase):
        raise NotImplementedError()
