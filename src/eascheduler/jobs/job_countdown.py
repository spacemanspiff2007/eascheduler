from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override
from whenever import TimeDelta, UTCDateTime

from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class CountdownJob(JobBase):
    def __init__(self, executor: ExecutorBase, secs: float, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)
        self._seconds: float = 0
        self.set_countdown(secs)    # Validate and set the countdown

    @override
    def update_next(self) -> None:
        self.set_loop_time(None, None)

    def set_countdown(self, secs: float) -> None:
        if not isinstance(secs, (int, float)):
            raise TypeError()
        if secs <= 0:
            raise ValueError()
        self._seconds = secs

    def reset(self) -> None:
        self._scheduler.set_job_time(self, UTCDateTime.now() + TimeDelta(seconds=self._seconds))
        self._scheduler.update_job(self)

    @override
    def job_resume(self):
        # Should call reset
        raise NotImplementedError()
