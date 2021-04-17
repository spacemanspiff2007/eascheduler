from __future__ import annotations

from datetime import timedelta
from typing import Optional, Union

from pendulum import DateTime, from_timestamp
from pendulum import UTC
from pendulum import now as get_now

from eascheduler.const import FAR_FUTURE, SKIP_EXECUTION
from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.executors import ExecutorBase
from eascheduler.schedulers import AsyncScheduler
from .job_datetime_base import DateTimeJobBase


class ReoccurringJob(DateTimeJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func)
        self._interval: Union[float, int] = FAR_FUTURE

    def _update_base_time(self):
        now = get_now(UTC).timestamp()

        while self._next_base < now:
            self._next_base += self._interval

        self._update_run_time()

    def _update_run_time(self, dt_start: Optional[DateTime] = None) -> DateTime:
        update_run_time = super()._update_run_time

        # Allow skipping certain occurrences
        next_run = update_run_time(dt_start)
        while next_run is SKIP_EXECUTION:
            self._next_run += self._interval
            next_run = update_run_time(from_timestamp(self._next_run))

        return next_run

    def interval(self, interval: Union[int, float, timedelta]) -> ReoccurringJob:
        """Set the interval at which the task will run.

        :param interval: interval in secs or a timedelta obj
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        if isinstance(interval, timedelta):
            interval = interval.total_seconds()
        assert interval > 0, interval

        self._interval = interval
        self._update_base_time()
        return self
