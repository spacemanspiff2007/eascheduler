from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from pendulum import DateTime

    from eascheduler.executor import ExecutorBase


class OneTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, execution_time: DateTime, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)
        self.execution_time: Final = execution_time

    @override
    def update_next(self) -> None:
        self.job_finish()

    @override
    def update_first(self) -> None:
        self._scheduler.set_job_time(self, self.execution_time)

    @override
    def job_pause(self):
        raise NotImplementedError()

    @override
    def job_resume(self):
        raise NotImplementedError()
