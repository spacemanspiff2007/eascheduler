from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class JobStoreBase:
    def add_job(self, job: JobBase):
        raise NotImplementedError()

    def remove_job(self, job: JobBase):
        raise NotImplementedError()

    def update_job(self, job: JobBase):
        raise NotImplementedError()

    def on_job_finished(self, job: JobBase):
        raise NotImplementedError()

    def on_job_executed(self, job: JobBase):
        raise NotImplementedError()
