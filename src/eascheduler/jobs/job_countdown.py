from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self, override
from whenever import Instant, TimeDelta

from eascheduler.errors.errors import JobNotLinkedToSchedulerError
from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class CountdownJob(JobBase):
    def __init__(self, executor: ExecutorBase, delta: TimeDelta, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)
        self._delta: TimeDelta = TimeDelta.ZERO
        self.set_countdown(delta)    # Validate and set the countdown

    @override
    def update_next(self) -> None:
        self.set_next_run(None)

    def set_countdown(self, secs: TimeDelta | float) -> None:
        if not isinstance(secs, TimeDelta):
            delta: Final = TimeDelta(seconds=secs)
        else:
            delta: Final = secs

        if not isinstance(delta, TimeDelta):
            raise TypeError()
        if delta <= TimeDelta.ZERO:
            raise ValueError()
        self._delta = delta

    def reset(self) -> None:
        if (scheduler := self._scheduler) is None:
            raise JobNotLinkedToSchedulerError()

        self.set_next_run(Instant.now() + self._delta)
        scheduler.update_job(self)

    @override
    def job_resume(self) -> Self:
        # Should call reset
        raise NotImplementedError()
