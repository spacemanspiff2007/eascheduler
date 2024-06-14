from __future__ import annotations  # noqa: I001

from enum import Enum
from typing import Final, overload
from typing import TYPE_CHECKING, Hashable, TypeVar, Generic

from pendulum import DateTime

from eascheduler.const import local_tz
from eascheduler.jobs.event_handler import JobEventHandler


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase

IdType = TypeVar('IdType', bound=Hashable)


class JobStatusEnum(str, Enum):
    CREATED = 'created'
    RUNNING = 'running'
    PAUSED = 'paused'
    FINISHED = 'finished'


STATUS_CREATED: Final = JobStatusEnum.CREATED
STATUS_RUNNING: Final = JobStatusEnum.RUNNING
STATUS_PAUSED: Final = JobStatusEnum.PAUSED
STATUS_FINISHED: Final = JobStatusEnum.FINISHED


class JobBase(Generic[IdType]):
    def __init__(self, executor: ExecutorBase, job_id: IdType | None = None):
        self.executor: Final = executor
        self.id: Final[IdType] = job_id if job_id is not None else id(self)

        # Job status
        self.status: JobStatusEnum = STATUS_CREATED

        # used to schedule the job
        self.next_time: float | None = None

        # for information only
        self.next_run: DateTime | None = None
        self.last_run: DateTime | None = None

        # callbacks
        self.on_update: Final = JobEventHandler()       # running | paused -> running | paused
        self.on_finished: Final = JobEventHandler()     # running | paused -> -> finished

    @overload
    def set_next_time(self, next_time: None, next_run: None):
        ...

    @overload
    def set_next_time(self, next_time: float, next_run: DateTime):
        ...

    def set_next_time(self, next_time, next_run):
        self.next_time = next_time
        self.next_run = next_run

        self.status = STATUS_RUNNING if next_time is not None else STATUS_PAUSED
        self.on_update.run(self)
        return self

    def update_next(self):
        raise NotImplementedError()

    def execute(self):
        self.executor.execute()
        self.last_run = DateTime.now(tz=local_tz)
        self.update_next()
        return self.status

    def __lt__(self, other):
        return self.next_time < other.next_time
