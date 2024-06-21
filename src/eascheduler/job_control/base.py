from __future__ import annotations

from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from eascheduler.jobs.base import JobBase


class HasJob(Protocol):
    @property
    def _job(self) -> JobBase: ...


class BaseControl:
    def __eq__(self: HasJob, other: HasJob):
        if (other_job := getattr(other, '_job', None)) is None:
            return False
        return self._job is other_job
