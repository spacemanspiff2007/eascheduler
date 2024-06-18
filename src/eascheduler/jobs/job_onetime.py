from __future__ import annotations

from datetime import timedelta
from time import monotonic
from typing import TYPE_CHECKING, Final

from pendulum import DateTime
from typing_extensions import override

from eascheduler.const import local_tz
from eascheduler.errors import ScheduledRunInThePastError
from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class OneTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, execution_time: float):
        super().__init__(executor)

        self.execution_time: Final = execution_time

    @override
    def update_next(self):
        self.job_finish()

    @override
    def update_first(self):
        self.set_next_time(
            self.execution_time, DateTime.now(tz=local_tz) + timedelta(self.execution_time - monotonic())
        )

    @override
    def job_stop(self):
        raise NotImplementedError()

    @override
    def job_resume(self):
        raise NotImplementedError()
