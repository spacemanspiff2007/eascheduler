from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class SchedulerBase:
    def add_job(self, job: JobBase):
        pass

    def remove_job(self, job: JobBase):
        pass

    def job_changed(self, job: JobBase):
        pass
