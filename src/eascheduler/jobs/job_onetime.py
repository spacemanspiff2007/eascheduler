from __future__ import annotations

from typing import TYPE_CHECKING, Final, NoReturn

from typing_extensions import override

from eascheduler.errors.errors import JobNotLinkedToSchedulerError
from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from whenever import UTCDateTime

    from eascheduler.executor import ExecutorBase


class OneTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, execution_time: UTCDateTime, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)
        self.execution_time: Final = execution_time

    @override
    def update_next(self) -> None:
        self.job_finish()

    @override
    def update_first(self) -> None:
        if (scheduler := self._scheduler) is None:
            raise JobNotLinkedToSchedulerError()
        scheduler.set_job_time(self, self.execution_time)

    @override
    def job_pause(self) -> NoReturn:
        raise NotImplementedError()

    @override
    def job_resume(self) -> NoReturn:
        raise NotImplementedError()
