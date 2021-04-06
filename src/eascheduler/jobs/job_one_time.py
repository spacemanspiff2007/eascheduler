from typing import Optional

from pendulum import DateTime

from eascheduler.errors import OneTimeJobCanNotBeSkipped
from .job_datetime_base import DateTimeJobBase
from eascheduler.const import SKIP_EXECUTION


class OneTimeJob(DateTimeJobBase):

    def _update_run_time(self, next_run: Optional[DateTime] = None) -> DateTime:
        res = super()._update_run_time()
        if res is SKIP_EXECUTION:
            raise OneTimeJobCanNotBeSkipped()
        return res
