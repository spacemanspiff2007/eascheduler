from typing import Final

from eascheduler.jobs import CountdownJob

from .base import BaseControl


class CountdownJobControl(BaseControl):
    def __init__(self, job: CountdownJob):
        self._job: Final = job

    def set_countdown(self, secs: float):
        self._job.set_countdown(secs)

    def cancel(self):
        self._job.job_finish()

    def stop(self):
        self._job.job_pause()

    def reset(self):
        self._job.reset()
