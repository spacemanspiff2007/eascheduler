from typing import Final

from eascheduler.jobs import DateTimeJob

from .base import BaseControl


class DateTimeJobControl(BaseControl):
    def __init__(self, job: DateTimeJob):
        self._job: Final = job

    def cancel(self):
        self._job.job_finish()

    def stop(self):
        self._job.job_stop()

    def resume(self):
        self._job.job_resume()
