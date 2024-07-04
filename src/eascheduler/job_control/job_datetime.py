from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self

from .base import BaseControl


if TYPE_CHECKING:
    from eascheduler.jobs import DateTimeJob


class DateTimeJobControl(BaseControl):
    def __init__(self, job: DateTimeJob):
        self._job: Final = job  # type: ignore[misc]

    def pause(self) -> Self:
        self._job.job_pause()
        return self

    def resume(self) -> Self:
        self._job.job_resume()
        return self
