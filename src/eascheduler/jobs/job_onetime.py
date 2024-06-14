from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from eascheduler.jobs.base import STATUS_FINISHED, JobBase


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class OneTimeJob(JobBase):
    def __init__(self, executor: ExecutorBase):
        super().__init__(executor)

    @override
    def update_next(self):
        self.status = STATUS_FINISHED
        self.next_time = None
        self.next_run = None

        self.on_finished.run(self)
