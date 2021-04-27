from datetime import timedelta, time as dt_time, datetime
from typing import Union

from eascheduler.jobs.job_base import ScheduledJobBase, get_first_timestamp


class OneTimeJob(ScheduledJobBase):

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        self._set_next_run(get_first_timestamp(first_run))

    def _schedule_next_run(self):
        self._parent = None
