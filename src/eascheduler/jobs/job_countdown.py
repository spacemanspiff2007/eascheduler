from __future__ import annotations

from datetime import datetime, timedelta
from typing import Union

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

    def expire(self, expire_time: Union[timedelta, float, int]) -> CountdownJob:
        """Set the time after which the job will be executed.

        :param expire_time: time
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        secs = expire_time.total_seconds() if isinstance(expire_time, timedelta) else expire_time
        assert secs > 0, secs

        self._expire = float(secs)
        return self

    def reset(self):
        if self._parent is None:
            raise JobAlreadyCanceledException()

        now = datetime.now(UTC).timestamp()
        self._set_next_run(now + self._expire)
        self._parent.add_job(self)

    def _update_base_time(self):
        self._set_next_run(FAR_FUTURE)
