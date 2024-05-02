from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Final, Literal

from pendulum import DateTime

from eascheduler.const import local_tz
from eascheduler.job_stores.base import JobStoreBase

if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


class JobBase:
    def __init__(self, executor: ExecutorBase, job_id: Any | None = None):
        self._executor: Final = executor
        self.job_id: Final = job_id if job_id is not None else id(job_id)

        # Job status
        self.status: Literal['created', 'running', 'paused', 'finished'] = 'created'

        # used to schedule the job
        self.next_time: float | None = None

        # for information only
        self.next_run: DateTime | None = None
        self.last_run: DateTime | None = None

        self.on_next_change: Callable[[JobBase], Any] | None = None

    def set_on_change(self, func: Callable[[JobBase], Any] | None = None):
        if self.on_next_change is not None and func is not None:
            raise ValueError()
        self.on_next_change = func

    def set_next_time(self, next_time: float | None, next_run: DateTime | None = None):

        old_time = self.next_time

        self.next_time = next_time
        self.next_run = next_run

        if old_time != next_time and (cb := self.on_next_change) is not None:
            cb(self)
        return self

    def update_next(self):
        raise NotImplementedError()

    def execute(self):
        self.update_next()
        self.last_run = DateTime.now(tz=local_tz)
        self._executor.execute()
        return self.status
