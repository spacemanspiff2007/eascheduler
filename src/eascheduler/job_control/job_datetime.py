from typing import Final

from eascheduler.jobs import DateTimeJob

from .base import BaseControl


class DateTimeJobControl(BaseControl):
    def __init__(self, job: DateTimeJob):
        self._job: Final = job

    def cancel(self):
        self._job.job_finish()

    def pause(self):
        self._job.job_pause()

    def resume(self):
        self._job.job_resume()
