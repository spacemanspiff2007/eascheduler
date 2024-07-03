from typing import Any, Callable, Final

from eascheduler.executor import ExecutorBase
from eascheduler.job_control import CountdownJobControl, DateTimeJobControl, OneTimeJobControl
from eascheduler.jobs import CountdownJob, DateTimeJob, OneTimeJob
from eascheduler.jobs.base import IdType
from eascheduler.producers.base import DateTimeProducerBase
from eascheduler.schedulers import SchedulerBase


class JobBuilder:
    def __init__(self, scheduler: SchedulerBase,
                 executor: Callable[[Callable, tuple, dict[str, Any]], ExecutorBase]) -> None:
        self._scheduler: Final = scheduler
        self._executor: Final = executor

    def countdown(self, secs, coro, *args, job_id: IdType | None = None, **kwargs) -> CountdownJobControl:
        job = CountdownJob(self._executor(coro, args, kwargs), secs, job_id=job_id)
        job.link_scheduler(self._scheduler)
        return CountdownJobControl(job)

    def once(self, instant, coro, *args, job_id: IdType | None = None, **kwargs) -> OneTimeJobControl:
        job = OneTimeJob(self._executor(coro, args, kwargs), instant, job_id=job_id)
        job.link_scheduler(self._scheduler)
        return OneTimeJobControl(job)

    def at(self, producer: DateTimeProducerBase, coro, *args, job_id: IdType | None = None, **kwargs) -> DateTimeJobControl:
        job = DateTimeJob(self._executor(coro, args, kwargs), producer, job_id=job_id)
        job.link_scheduler(self._scheduler)
        return DateTimeJobControl(job)
