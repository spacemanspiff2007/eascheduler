from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self

from .base import BaseControl


if TYPE_CHECKING:
    from eascheduler.jobs import CountdownJob


class CountdownJobControl(BaseControl):
    def __init__(self, job: CountdownJob) -> None:
        self._job: Final[CountdownJob] = job  # type: ignore[misc]

    def set_countdown(self, secs: float) -> Self:
        """Set the countdown time

        :param secs: Seconds that will be used for the next reset call
        """
        self._job.set_countdown(secs)
        return self

    def stop(self) -> Self:
        """Stop the countdown"""
        self._job.job_pause()
        return self

    def reset(self) -> Self:
        """Start the countdown again"""
        self._job.reset()
        return self
