from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override
from whenever import UTCDateTime

from eascheduler.errors.errors import JobNotLinkedToSchedulerError
from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase
    from eascheduler.producers.base import DateTimeProducerBase


class DateTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, producer: DateTimeProducerBase, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)

        self.producer: Final = producer

    @override
    def update_next(self) -> None:
        if (scheduler := self._scheduler) is None:
            raise JobNotLinkedToSchedulerError()

        next_run = self.producer.get_next(UTCDateTime.now())
        scheduler.set_job_time(self, next_run)
