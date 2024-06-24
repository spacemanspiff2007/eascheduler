from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self

from .base import BaseControl


if TYPE_CHECKING:
    from eascheduler.jobs import CountdownJob


class CountdownJobControl(BaseControl):
    def __init__(self, job: CountdownJob):
        self._job: Final[CountdownJob] = job

    def set_countdown(self, secs: float) -> Self:
        self._job.set_countdown(secs)
        return self

    def stop(self) -> Self:
        self._job.job_pause()
        return self

    def reset(self) -> Self:
        self._job.reset()
        return self
