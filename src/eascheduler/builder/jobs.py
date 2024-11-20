from collections.abc import Awaitable, Callable
from typing import Any, Final

from eascheduler.builder.helper import (
    HINT_INSTANT,
    HINT_POS_TIMEDELTA,
    get_instant,
    get_pos_timedelta_secs,
)
from eascheduler.builder.triggers import TriggerObject, _get_producer
from eascheduler.executor import ExecutorBase
from eascheduler.job_control import CountdownJobControl, DateTimeJobControl, OneTimeJobControl
from eascheduler.job_stores import JobStoreBase
from eascheduler.jobs import CountdownJob, DateTimeJob, OneTimeJob
from eascheduler.jobs.base import IdType
from eascheduler.schedulers import SchedulerBase


# noinspection PyProtectedMember
class JobBuilder:
    def __init__(self, scheduler: SchedulerBase,
                 executor: Callable[[Callable, tuple, dict[str, Any]], ExecutorBase],
                 job_store: JobStoreBase | None = None) -> None:
        self._scheduler: Final = scheduler
        self._executor: Final = executor
        self._job_store: Final = job_store

    def countdown(self, secs: HINT_POS_TIMEDELTA, coro_func: Callable[..., Awaitable[Any]],
                  *args: Any, job_id: IdType | None = None, **kwargs: Any) -> CountdownJobControl:
        """Create a job that count town a certain time and then execute.

        :param secs: countdown time in seconds
        :param coro_func: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id: |param_job_id|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = CountdownJob(self._executor(coro_func, args, kwargs), get_pos_timedelta_secs(secs), job_id=job_id)
        job.link_scheduler(self._scheduler)
        if self._job_store is not None:
            self._job_store.add_job(job)
        return CountdownJobControl(job)

    def once(self, instant: HINT_INSTANT, coro_func: Callable[..., Awaitable[Any]],
             *args: Any, job_id: IdType | None = None, **kwargs: Any) -> OneTimeJobControl:
        """Create a job that runs once.

        :param instant: countdown time in seconds
        :param coro_func: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id: |param_job_id|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = OneTimeJob(self._executor(coro_func, args, kwargs), get_instant(instant), job_id=job_id)
        job.link_scheduler(self._scheduler)
        if self._job_store is not None:
            self._job_store.add_job(job)
        return OneTimeJobControl(job)

    def at(self, trigger: TriggerObject, coro_func: Callable[..., Awaitable[Any]],
           *args: Any, job_id: IdType | None = None, **kwargs: Any) -> DateTimeJobControl:
        """Create a job that will run at a specified time.

        :param trigger:
        :param coro_func: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param job_id: |param_job_id|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = DateTimeJob(self._executor(coro_func, args, kwargs), _get_producer(trigger), job_id=job_id)
        job.link_scheduler(self._scheduler)
        if self._job_store is not None:
            self._job_store.add_job(job)
        return DateTimeJobControl(job)
