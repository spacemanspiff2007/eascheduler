from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self


if TYPE_CHECKING:
    from pendulum import DateTime

    from eascheduler.jobs.base import JobBase


class SchedulerBase:
    __slots__ = ()

    def add_job(self, job: JobBase) -> Self:
        raise NotImplementedError()

    def remove_job(self, job: JobBase) -> Self:
        raise NotImplementedError()

    def update_job(self, job: JobBase) -> Self:
        raise NotImplementedError()

    def set_job_time(self, job: JobBase, next_time: DateTime | None) -> Self:
        raise NotImplementedError()
