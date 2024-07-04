from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .base import BaseControl


if TYPE_CHECKING:
    from eascheduler.jobs import OneTimeJob


class OneTimeJobControl(BaseControl):
    def __init__(self, job: OneTimeJob) -> None:
        self._job: Final = job  # type: ignore[misc]
