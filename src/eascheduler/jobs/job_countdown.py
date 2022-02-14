from __future__ import annotations

from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from typing import Union

from pendulum import now as get_now
from pendulum import UTC

from eascheduler.const import FAR_FUTURE
from eascheduler.errors import JobAlreadyCanceledException
from eascheduler.executors.executor import ExecutorBase
from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler


class CountdownJob(ScheduledJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func)
        self._expire: float = 0.0

    def countdown(self, time: Union[timedelta, float, int]) -> CountdownJob:
        """Set the time after which the job will be executed.

        :param time: time
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        secs = time.total_seconds() if isinstance(time, timedelta) else time
        assert secs > 0, secs

        self._expire = float(secs)
        return self

    def reset(self):
        if self._parent is None:
            raise JobAlreadyCanceledException()

        now = get_now(UTC).timestamp()
        self._set_next_run(now + self._expire)
        self._parent.add_job(self)

    def stop(self):
        """Stops the countdown so it can be started again with a call to reset"""
        if self._parent is None:
            raise JobAlreadyCanceledException()
        self._set_next_run(FAR_FUTURE)

    def _schedule_next_run(self):
        self._set_next_run(FAR_FUTURE)

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        pass
