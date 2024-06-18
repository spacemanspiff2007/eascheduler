from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Final, override

from pendulum import DateTime

from eascheduler.const import local_tz
from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase
    from eascheduler.producers.base import ProducerBase


class DateTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase, producer: ProducerBase):
        super().__init__(executor)

        self.producer: Final = producer

    @override
    def update_next(self):
        now = DateTime.now(tz=local_tz)

        next_run = self.producer.get_next(now)
        next_time = next_run.diff(DateTime.now(tz=local_tz)).total_seconds() - monotonic()

        self.set_next_time(next_time, next_run)

    @override
    def stop(self):
        self.set_next_time(None, None)

    @override
    def resume(self):
        self.update_next()
