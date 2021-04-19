from datetime import datetime as dt_datetime
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta
from typing import Union, Type, Iterable

from eascheduler.executors import ExecutorBase
from eascheduler.jobs import OneTimeJob, CountdownJob, ReoccurringJob, DayOfWeekJob, \
    SunriseJob, SunsetJob, DuskJob, DawnJob
from eascheduler.schedulers import AsyncScheduler


class SchedulerView:
    def __init__(self, scheduler: AsyncScheduler, executor: Type[ExecutorBase]):
        self._scheduler: AsyncScheduler = scheduler
        self._executor: Type[ExecutorBase] = executor

    def at(self, time: Union[None, dt_datetime, dt_timedelta, dt_time, int, float],
           callback, *args, **kwargs) -> OneTimeJob:
        """Create a a job that will run at a specified time.

        :param time:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = OneTimeJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._initialize_base_time(time)
        job._update_run_time()
        return job

    def countdown(self, expire_time: Union[dt_timedelta, float, int], callback, *args, **kwargs) -> CountdownJob:
        """Run a job a specific time after calling ``reset()`` of the job.
        Another subsequent call to ``reset()`` will start the countdown again.

        :param expire_time: countdown in seconds or a timedelta obj
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = CountdownJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job.countdown(expire_time)
        self._scheduler.add_job(job)
        return job

    def every(self, start_time: Union[None, dt_datetime, dt_timedelta, dt_time, int, float],
              interval: Union[int, float, dt_timedelta], callback, *args, **kwargs) -> ReoccurringJob:
        """Create a job that will run at a specific interval.

        :param start_time: First execution time
        :param interval: Interval how the job is repeated
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = ReoccurringJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._initialize_base_time(start_time)
        job.interval(interval)
        return job

    def on_day_of_week(self, time: Union[dt_time, dt_datetime], weekdays: Union[str, Iterable[Union[str, int]]],
                       callback, *args, **kwargs) -> DayOfWeekJob:
        """Create a job that will run at a certain time on certain days during the week.

        :param time: Time when the job will run
        :param weekdays: Day group names  (e.g. ``'all'``, ``'weekend'``, ``'workdays'``), an iterable with
                         day names (e.g. ``['Mon', 'Fri']``) or an iterable with the isoweekday values
                         (e.g. ``[1, 5]``).
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = DayOfWeekJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job.time(time)
        job.weekdays(weekdays)
        return job

    def on_weekends(self, time: Union[dt_time, dt_datetime], callback, *args, **kwargs) -> DayOfWeekJob:
        """Create a job that will run at a certain time on weekends.

        :param time: Time when the job will run
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        return self.on_day_of_week(time, 'weekend', callback, *args, **kwargs)

    def on_workdays(self, time: Union[dt_time, dt_datetime], callback, *args, **kwargs) -> DayOfWeekJob:
        """Create a job that will run at a certain time on workdays.

        :param time: Time when the job will run
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        return self.on_day_of_week(time, 'workdays', callback, *args, **kwargs)

    def on_sunrise(self, callback, *args, **kwargs) -> SunriseJob:
        """Create a job that will run on sunrise, requires a location to be set

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = SunriseJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._update_base_time()
        return job

    def on_sunset(self, callback, *args, **kwargs) -> SunsetJob:
        """Create a job that will run on sunset, requires a location to be set

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = SunsetJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._update_base_time()
        return job

    def on_sun_dawn(self, callback, *args, **kwargs) -> DawnJob:
        """Create a job that will run on dawn, requires a location to be set

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = DawnJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._update_base_time()
        return job

    def on_sun_dusk(self, callback, *args, **kwargs) -> DuskJob:
        """Create a job that will run on dusk, requires a location to be set

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        :return: Created job
        """
        job = DuskJob(self._scheduler, self._executor(callback, *args, **kwargs))
        job._update_base_time()
        return job
