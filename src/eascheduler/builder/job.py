from collections.abc import Awaitable, Callable
from typing import Any, Final

from eascheduler.builder.helper import HINT_INSTANT, get_instant
from eascheduler.builder.triggers import TriggerObject
from eascheduler.executor import ExecutorBase
from eascheduler.job_control import CountdownJobControl, DateTimeJobControl, OneTimeJobControl
from eascheduler.jobs import CountdownJob, DateTimeJob, OneTimeJob
from eascheduler.jobs.base import IdType
from eascheduler.schedulers import SchedulerBase


# noinspection PyProtectedMember
class JobBuilder:
    def __init__(self, scheduler: SchedulerBase,
                 executor: Callable[[Callable, tuple, dict[str, Any]], ExecutorBase]) -> None:
        self._scheduler: Final = scheduler
        self._executor: Final = executor

    def countdown(self, secs: float, coro_func: Callable[..., Awaitable[Any]],
                  *args: Any, job_id: IdType | None = None, **kwargs: Any) -> CountdownJobControl:
        job = CountdownJob(self._executor(coro_func, args, kwargs), secs, job_id=job_id)
        job.link_scheduler(self._scheduler)
        return CountdownJobControl(job)

    def once(self, instant: HINT_INSTANT, coro_func: Callable[..., Awaitable[Any]],
             *args: Any, job_id: IdType | None = None, **kwargs: Any) -> OneTimeJobControl:
        job = OneTimeJob(self._executor(coro_func, args, kwargs), get_instant(instant), job_id=job_id)
        job.link_scheduler(self._scheduler)
        return OneTimeJobControl(job)

    def at(self, trigger: TriggerObject, coro_func: Callable[..., Awaitable[Any]],
           *args: Any, job_id: IdType | None = None, **kwargs: Any) -> DateTimeJobControl:
        """Create a job that will run at a specified time.

        :param trigger:
        :param coro_func: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id:
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = DateTimeJob(self._executor(coro_func, args, kwargs), trigger._producer, job_id=job_id)
        job.link_scheduler(self._scheduler)
        return DateTimeJobControl(job)
