from __future__ import annotations

from typing import TYPE_CHECKING, Final

from pendulum import DateTime
from typing_extensions import override

from eascheduler.const import local_tz
from eascheduler.jobs.base import IdType, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase
    from eascheduler.producers.base import ProducerBase


class DateTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, producer: ProducerBase, *, job_id: IdType | None = None) -> None:
        super().__init__(executor, job_id=job_id)

        self.producer: Final = producer

    @override
    def update_next(self) -> None:
        next_run = self.producer.get_next(DateTime.now(tz=local_tz))
        self._scheduler.set_job_time(self, next_run)
