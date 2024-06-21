from typing import Final

from eascheduler.jobs import OneTimeJob

from .base import BaseControl


class OneTimeJobControl(BaseControl):
    def __init__(self, job: OneTimeJob):
        self._job: Final = job

    def cancel(self):
        self._job.job_finish()
