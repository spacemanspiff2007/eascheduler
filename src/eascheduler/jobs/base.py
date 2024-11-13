from __future__ import annotations

from collections.abc import Callable, Hashable
from enum import Enum
from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import Self
from whenever import Instant

from eascheduler.errors.errors import JobAlreadyFinishedError, ScheduledRunInThePastError
from eascheduler.jobs.event_handler import JobCallbackHandler


if TYPE_CHECKING:
    from eascheduler.executor import ExecutorBase
    from eascheduler.schedulers import SchedulerBase

IdType = TypeVar('IdType', bound=Hashable)


def _default_job_id_func(job: JobBase) -> Hashable:
    return id(job)


JOB_ID_FUNC: Callable[[JobBase], Hashable] = _default_job_id_func


class JobStatusEnum(str, Enum):
    CREATED = 'created'
    RUNNING = 'running'
    PAUSED = 'paused'
    FINISHED = 'finished'

    @property
    def is_running(self) -> bool:
        """True if the job is running"""
        return self is STATUS_RUNNING

    @property
    def is_paused(self) -> bool:
        """True if the job is paused"""
        return self is STATUS_PAUSED

    @property
    def is_finished(self) -> bool:
        """True if the job is finished"""
        return self is STATUS_FINISHED


STATUS_CREATED: Final = JobStatusEnum.CREATED
STATUS_RUNNING: Final = JobStatusEnum.RUNNING
STATUS_PAUSED: Final = JobStatusEnum.PAUSED
STATUS_FINISHED: Final = JobStatusEnum.FINISHED


class JobBase(Generic[IdType]):
    def __init__(self, executor: ExecutorBase, *, job_id: IdType | None = None) -> None:
        super().__init__()
        self.executor: Final = executor
        self._id: Final[IdType] = job_id if job_id is not None else JOB_ID_FUNC(self)
        self._scheduler: SchedulerBase | None = None

        # Job status
        self.status: JobStatusEnum = STATUS_CREATED

        # Used to schedule the job
        self.next_run: Instant | None = None
        # for information only
        self.last_run: Instant | None = None

        # callbacks
        self.on_update: Final = JobCallbackHandler()       # running | paused -> running | paused
        self.on_finished: Final = JobCallbackHandler()     # running | paused -> finished

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

    def set_next_run(self, next_run: Instant | None) -> Self:
        if next_run is None:
            self.next_run = next_run
            self.status = STATUS_PAUSED
        else:
            if next_run < Instant.now().subtract(milliseconds=100):
                raise ScheduledRunInThePastError()

            self.next_run = next_run
            self.status = STATUS_RUNNING

        # trigger callbacks
        self.on_update.run(self)
        return self

    def update_first(self) -> None:
        self.update_next()

    def update_next(self) -> None:
        raise NotImplementedError()

    def execute(self) -> JobStatusEnum:
        self.executor.execute()
        self.last_run = Instant.now()
        self.update_next()
        return self.status

    def __lt__(self, other_job: object) -> bool:
        if (other := other_job.next_run) is None:
            return True
        if (this := self.next_run) is None:
            return False
        return this < other

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} status={self.status.value} next_run={self.next_run}>'

    def job_finish(self) -> Self:
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self._scheduler.remove_job(self)
        self._scheduler = None

        self.status = STATUS_FINISHED
        self.next_run = None

        self.on_finished.run(self)
        return self

    def job_pause(self) -> Self:
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self._scheduler.remove_job(self)
        self.set_next_run(None)
        return self

    def job_resume(self) -> Self:
        if self.status is STATUS_FINISHED:
            raise JobAlreadyFinishedError()

        self.update_next()
        self._scheduler.update_job(self)
        return self
