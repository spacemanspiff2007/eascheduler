from __future__ import annotations

from typing import TypeVar

from eascheduler.jobs.base import JobBase


JOB_TYPE = TypeVar('JOB_TYPE', bound=JobBase)


class JobStoreBase:
    def add_job(self, job: JOB_TYPE) -> JOB_TYPE:
        raise NotImplementedError()
