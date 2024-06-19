from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Generic, TypeAlias, TypeVar

from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from eascheduler.schedulers import SchedulerBase


KEY_TYPE = TypeVar('KEY_TYPE')
JOB_TYPE = TypeVar('JOB_TYPE', bound=JobBase)


class SimpleJobIdStore(Generic[KEY_TYPE, JOB_TYPE]):
    __slots__ = ('_scheduler', '_jobs')

    def __init__(self, scheduler: SchedulerBase) -> None:
        self._scheduler: Final = scheduler
        self._jobs: Final[dict[KEY_TYPE, JOB_TYPE]] = {}

    def add_job(self, job: JOB_TYPE):
        # remove job from scheduler if it already exists
        if (job_id := job.id) in self._jobs:
            msg = f'Duplicate key: {job_id}'
            raise KeyError(msg)

        self._jobs[job_id] = job
        self._scheduler.add_job(job)

    def remove_job(self, job: JOB_TYPE) -> JOB_TYPE:
        job = self._jobs.pop(job.id)
        self._scheduler.remove_job(job)
        return job

    def update_job(self, job: JobBase) -> None:
        self._scheduler.update_job(job)

    # noinspection PyShadowingBuiltins
    def pop(self, id: Any) -> JOB_TYPE:
        return self.remove_job(self._jobs[id])

    # noinspection PyShadowingBuiltins
    def get(self, id: Any) -> JOB_TYPE | None:
        return self._jobs.get(id)

    def __getitem__(self, item: KEY_TYPE) -> JOB_TYPE:
        return self._jobs[item]

    def __contains__(self, item: KEY_TYPE) -> bool:
        return item in self._jobs

    def items(self):
        return self._jobs.items()
