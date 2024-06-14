from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class SchedulerBase:
    __slots__ = ()

    def add_job(self, job: JobBase):
        pass

    def remove_job(self, job: JobBase):
        pass

    def update_job(self, job: JobBase):
        pass
