from __future__ import annotations

from datetime import timedelta
from time import monotonic
from typing import TYPE_CHECKING

from pendulum import DateTime
from typing_extensions import override

from eascheduler.const import local_tz
from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class CountdownJob(JobBase):
    def __init__(self, executor: ExecutorBase, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)
        self._seconds: float = 0

    @override
    def update_next(self) -> None:
        self.set_next_time(None, None)
        self._scheduler.update_job(self)

    def countdown(self, secs: float) -> None:
        assert secs > 0, secs
        self._seconds = secs

    def reset(self) -> None:
        next_time = monotonic() + self._seconds
        self.set_next_time(next_time, DateTime.now(tz=local_tz) + timedelta(next_time - monotonic()))
        self._scheduler.update_job(self)

    @override
    def job_resume(self):
        # Should call reset
        raise NotImplementedError()
