from __future__ import annotations

from datetime import timedelta
from time import monotonic
from typing import TYPE_CHECKING

from pendulum import DateTime
from typing_extensions import override

from eascheduler.const import local_tz
from eascheduler.jobs.base import JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class CountdownJob(JobBase):
    def __init__(self, executor: ExecutorBase):
        super().__init__(executor)

        self._seconds: float = 0

    @override
    def update_next(self):
        self.set_next_time(None, None)

    def countdown(self, secs: float):
        assert secs > 0, secs
        self._seconds = secs

    def reset(self):
        next_time = monotonic() + self._seconds
        self.set_next_time(next_time, DateTime.now(tz=local_tz) + timedelta(next_time - monotonic()))

    @override
    def stop(self):
        self.set_next_time(None, None)

    @override
    def resume(self):
        self.update_next()
