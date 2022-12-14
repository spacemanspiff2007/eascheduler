from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from typing import Union

from eascheduler.const import FAR_FUTURE
from eascheduler.jobs.job_base import get_first_timestamp, ScheduledJobBase


class OneTimeJob(ScheduledJobBase):

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        self._set_next_run(get_first_timestamp(first_run))

    def _schedule_next_run(self):
        self._next_run = FAR_FUTURE
        self._parent = None
