from __future__ import annotations  # noqa: I001

from typing import TYPE_CHECKING, Final, Literal, Hashable, TypeVar, Generic
from uuid import uuid4

from pendulum import DateTime

from eascheduler.const import local_tz

if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase


IdType = TypeVar('IdType', bound=Hashable)


class JobBase(Generic[IdType]):
    def __init__(self, executor: ExecutorBase, job_id: IdType | None = None):
        self._executor: Final = executor
        self._job_id: Final = job_id if job_id is not None else id(self)

        # Job status
        self.status: Literal['created', 'running', 'paused', 'finished'] = 'created'

        # used to schedule the job
        self.next_time: float | None = None

        # for information only
        self.next_run: DateTime | None = None
        self.last_run: DateTime | None = None

    @property
    def id(self) -> IdType:
        return self._job_id

    def set_next_time(self, next_time: float | None, next_run: DateTime | None = None):
        self.next_time = next_time
        self.next_run = next_run
        return self

    def update_next(self):
        raise NotImplementedError()

    def execute(self):
        self.update_next()
        self.last_run = DateTime.now(tz=local_tz)
        self._executor.execute()
        return self.status

    def __lt__(self, other):
        return self.next_time < other.next_time
