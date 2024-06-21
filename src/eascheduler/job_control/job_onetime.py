from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self

from .base import BaseControl


if TYPE_CHECKING:
    from eascheduler.jobs import OneTimeJob


class OneTimeJobControl(BaseControl):
    def __init__(self, job: OneTimeJob):
        self._job: Final = job

    def cancel(self) -> Self:
        self._job.job_finish()
        return self
