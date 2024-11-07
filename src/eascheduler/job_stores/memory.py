from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import override

from eascheduler.job_stores.base import JobStoreBase
from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from collections.abc import dict_items


JOB_ID_TYPE = TypeVar('JOB_ID_TYPE', bound=Hashable)
JOB_TYPE = TypeVar('JOB_TYPE', bound=JobBase)


class InMemoryStore(JobStoreBase, Generic[JOB_ID_TYPE, JOB_TYPE]):
    def __init__(self) -> None:
        self._jobs: Final[dict[JOB_ID_TYPE, JOB_TYPE]] = {}

    @override
    def add_job(self, job: JOB_TYPE) -> JOB_TYPE:
        # remove job from scheduler if it already exists
        if (job_id := job.id) in self._jobs:
            msg = f'Duplicate key: {job_id}'
            raise KeyError(msg)

        self._jobs[job_id] = job
        job.on_finished.register(self._job_finished)
        return job

    def _job_finished(self, job: JOB_TYPE) -> None:
        self._jobs.pop(job.id)

    def pop(self, job_id: JOB_ID_TYPE) -> JOB_TYPE:
        return self._jobs.pop(job_id)

    def get(self, job_id: JOB_ID_TYPE) -> JOB_TYPE | None:
        return self._jobs.get(job_id)

    def __getitem__(self, job_id: JOB_ID_TYPE) -> JOB_TYPE:
        return self._jobs[job_id]

    def __contains__(self, job_id: JOB_ID_TYPE) -> bool:
        return job_id in self._jobs

    def __len__(self) -> int:
        return len(self._jobs)

    def items(self) -> dict_items[JOB_ID_TYPE, JOB_TYPE]:
        return self._jobs.items()
