from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Generic, TypeAlias, TypeVar

from typing_extensions import override

from eascheduler.job_stores.base import JobStoreBase
from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from eascheduler.schedulers import SchedulerBase


KEY_TYPE: TypeAlias = TypeVar('KEY_TYPE')
JOB_TYPE: TypeAlias = TypeVar('JOB_TYPE', bound=JobBase)


class SimpleJobIdStore(JobStoreBase, Generic[KEY_TYPE, JOB_TYPE]):
    __slots__ = ('_scheduler', '_jobs')

    def __init__(self, scheduler: SchedulerBase):
        self._scheduler: Final = scheduler
        self._jobs: Final[dict[KEY_TYPE, JOB_TYPE]] = {}

    @override
    def add_job(self, job: JOB_TYPE):
        # remove job from scheduler if it already exists
        if (job_id := job.job_id) in self._jobs:
            self._scheduler.remove_job(self._jobs[job_id])

        self._jobs[job_id] = job
        self._scheduler.add_job(job)

    @override
    def remove_job(self, job: JOB_TYPE):
        job = self._jobs.pop(job.job_id)
        self._scheduler.remove_job(job)

    @override
    def update_job(self, job: JobBase):
        self._scheduler.update_job(job)

    @override
    def on_job_finished(self, job: JOB_TYPE):
        self._jobs.pop(job.job_id)

    @override
    def on_job_executed(self, job: JobBase):
        pass

    # noinspection PyShadowingBuiltins
    def pop(self, id: Any) -> None:
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
