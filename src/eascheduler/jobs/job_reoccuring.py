from __future__ import annotations

from datetime import timedelta
from typing import Union

from pendulum import DateTime
from pendulum import now as get_now
from pendulum import UTC

from eascheduler.const import FAR_FUTURE
from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.executors import ExecutorBase
from eascheduler.jobs.job_base_datetime import DateTimeJobBase
from eascheduler.schedulers import AsyncScheduler


class ReoccurringJob(DateTimeJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func)
        self._interval: Union[float, int] = FAR_FUTURE

    def _schedule_next_run(self):
        now = get_now(UTC).timestamp()
        while self._next_run_base < now or self._next_run_base <= self._last_run_base:
            self._next_run_base += self._interval

        self._apply_boundaries()

    def _advance_time(self, utc_dt: DateTime) -> DateTime:
        return utc_dt + timedelta(seconds=self._interval)

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

        if self._next_run_base < FAR_FUTURE:
            self._schedule_next_run()
        return self
