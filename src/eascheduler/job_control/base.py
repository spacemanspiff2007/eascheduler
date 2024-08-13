from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self


if TYPE_CHECKING:
    from collections.abc import Hashable
    from datetime import datetime as dt_datetime

    from eascheduler.jobs.base import JobBase, JobStatusEnum


class BaseControl:
    _job: JobBase

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseControl):
            return False
        return self._job is other._job

    def cancel(self: Self) -> Self:
        """Cancel the job"""

        self._job.job_finish()
        return self

    @property
    def id(self) -> Hashable:
        """Get the job's id"""

        return self._job.id

    @property
    def status(self) -> JobStatusEnum:
        """Get the status of the job"""

        return self._job.status

    @property
    def next_run_datetime(self) -> dt_datetime | None:
        """Get the next run time as a naive datetime object (without timezone set) or None if not scheduled"""

        if (nr := self._job.next_run) is None:
            return None
        return nr.to_system_tz().local().py_datetime()

    @property
    def last_run_datetime(self) -> dt_datetime | None:
        """Get the last run time as a naive datetime object (without timezone set) or None if yet run"""

        if (nr := self._job.last_run) is None:
            return None
        return nr.to_system_tz().local().py_datetime()
