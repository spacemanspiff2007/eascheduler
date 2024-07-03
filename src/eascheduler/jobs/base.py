from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Final, Generic, Hashable, TypeVar, overload

from typing_extensions import Self
from whenever import UTCDateTime

from eascheduler.errors.errors import JobAlreadyFinishedError
from eascheduler.jobs.event_handler import JobEventHandler


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase
    from eascheduler.schedulers import SchedulerBase

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
    def __init__(self, executor: ExecutorBase, *, job_id: IdType | None = None) -> None:
        super().__init__()
        self.executor: Final = executor
        self._id: Final[IdType] = job_id if job_id is not None else id(self)
        self._scheduler: SchedulerBase | None = None

        # Job status
        self.status: JobStatusEnum = STATUS_CREATED

        # used to schedule the job
        self.loop_time: float | None = None

        # for information only
        self.next_run: UTCDateTime | None = None
        self.last_run: UTCDateTime | None = None

        # callbacks
        self.on_update: Final = JobEventHandler()       # running | paused -> running | paused
        self.on_finished: Final = JobEventHandler()     # running | paused -> -> finished

    @property
    def id(self) -> IdType:
        return self._id

    def link_scheduler(self, scheduler: SchedulerBase) -> Self:
        if self._scheduler is scheduler:
            return self

        if self._scheduler is not None:
            msg = 'Job already linked to a scheduler'
            raise ValueError(msg)

        self._scheduler = scheduler
        self.update_first()
        self._scheduler.add_job(self)
        return self

    @overload
    def set_loop_time(self, loop_time: None, next_run: None) -> Self:
        ...

    @overload
    def set_loop_time(self, loop_time: float, next_run: UTCDateTime) -> Self:
        ...

    def set_loop_time(self, loop_time, next_run) -> Self:
        self.loop_time = loop_time
        self.next_run = next_run

        self.status = STATUS_RUNNING if loop_time is not None else STATUS_PAUSED
        self.on_update.run(self)
        return self

    def update_first(self) -> None:
        self.update_next()

    def update_next(self):
        raise NotImplementedError()

    def execute(self):
        self.executor.execute()
        self.last_run = UTCDateTime.now()
        self.update_next()
        return self.status

    def __lt__(self, other_job) -> bool:
        if (other := other_job.loop_time) is None:
            return True
        if (this := self.loop_time) is None:
            return False
        return this < other

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id!r} status={self.status!s} next_run={self.next_run}>'

    def job_finish(self):
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self._scheduler.remove_job(self)
        self._scheduler = None

        self.status = STATUS_FINISHED
        self.loop_time = None
        self.next_run = None

        self.on_finished.run(self)
        return self

    def job_pause(self):
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self._scheduler.remove_job(self)
        self.set_loop_time(None, None)

    def job_resume(self):
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self.update_next()
        self._scheduler.update_job(self)
