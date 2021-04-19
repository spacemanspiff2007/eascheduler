from __future__ import annotations

from datetime import datetime, timedelta, time
from random import uniform
from typing import Callable, Optional, Tuple, Union

from pendulum import UTC, from_timestamp, instance, DateTime
from pendulum import now as get_now

from eascheduler.const import SKIP_EXECUTION, _Execution
from eascheduler.const import local_tz, FAR_FUTURE
from eascheduler.errors import JobAlreadyCanceledException, FirstRunInThePastError
from eascheduler.executors.executor import ExecutorBase
from eascheduler.jobs.job_base import ScheduledJobBase
from eascheduler.schedulers import AsyncScheduler

try:
    from typing import Literal
except ImportError:
    from typing import Type
    Literal = Type


class DateTimeJobBase(ScheduledJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func)

        # base time when the job gets executed
        self._next_base: float = FAR_FUTURE

        # boundaries
        self._earliest: Optional[time] = None
        self._latest: Optional[time] = None
        self._offset: Optional[timedelta] = None
        self._jitter: Optional[Tuple[float, float]] = None
        self._boundary_func: Optional[Callable[[datetime], datetime]] = None

    def earliest(self, time_obj: Optional[time]) -> DateTimeJobBase:
        """Set earliest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run earlier
        """
        assert isinstance(time_obj, time) or time_obj is None, type(time_obj)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._earliest != time_obj
        self._earliest = time_obj
        if changed:
            self._update_run_time()
        return self

    def latest(self, time_obj: Optional[time]) -> DateTimeJobBase:
        """Set latest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run later
        """
        assert isinstance(time_obj, time) or time_obj is None, type(time_obj)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._latest != time_obj
        self._latest = time_obj
        if changed:
            self._update_run_time()
        return self

    def offset(self, timedelta_obj: Optional[timedelta]) -> DateTimeJobBase:
        """Set a constant offset to the calculation of the next run. ``None`` will disable the offset.

        :param timedelta_obj: constant offset
        """
        assert isinstance(timedelta_obj, timedelta) or timedelta_obj is None, type(timedelta_obj)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._offset != timedelta_obj
        self._offset = timedelta_obj
        if changed:
            self._update_run_time()
        return self

    def jitter(self, start: Optional[Union[int, float]], stop: Optional[Union[int, float]] = None) -> DateTimeJobBase:
        """Add a random jitter per call in the interval [start <= secs <= stop] to the next run.
        If stop is omitted start must be positive and the interval will be [-start <= secs <= start]
        Passing ``None`` as start will disable jitter.

        :param start: Interval start or ``None`` to disable jitter
        :param stop: Interval stop or ``None`` to build interval based on start
        """
        assert isinstance(start, (int, float)) or start is None, type(start)
        assert isinstance(stop, (int, float)) or stop is None, type(start)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        jitter = None
        if start is not None:
            if stop is None:
                stop = abs(start)
                start = stop * -1

            assert start < stop, f'{start} < {stop}'
            jitter = (start, stop)

        changed = self._jitter != jitter
        self._jitter = jitter
        if changed:
            self._update_run_time()
        return self

    def boundary_func(self, func: Optional[Callable[[datetime], datetime]]) -> DateTimeJobBase:
        """Add a function which will be called when the datetime changes. Use this to implement custom boundaries.
        Use ``None`` to disable the boundary function.

        :param func: Function which returns a datetime obj, arg is a datetime with the next run time. Return
                     ``SKIP_EXECUTION`` together with a reoccurring job to skip the proposed run time.
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._boundary_func != func
        self._boundary_func = func
        if changed:
            self._update_run_time()
        return self

    def _update_run_time(self, dt_start: Optional[DateTime] = None) -> Union[DateTime, Literal[_Execution.SKIP]]:
        assert dt_start is None or dt_start.timezone is UTC, dt_start.timezone

        # Starting point is always the next call from UTC
        next_run: DateTime = from_timestamp(self._next_base) if dt_start is None else dt_start

        # custom boundaries first
        if self._boundary_func is not None:
            next_run = next_run.in_timezone(local_tz).naive()
            custom_obj = self._boundary_func(next_run)
            if custom_obj is SKIP_EXECUTION:
                return SKIP_EXECUTION
            next_run = instance(custom_obj, local_tz).astimezone(local_tz).in_timezone(UTC)

        if self._offset is not None:
            next_run += self._offset  # offset doesn't have to be localized

        if self._jitter is not None:
            next_run += timedelta(seconds=uniform(self._jitter[0], self._jitter[1]))

        if self._earliest is not None:
            earliest = next_run.in_timezone(local_tz)
            earliest = earliest.set(hour=self._earliest.hour, minute=self._earliest.minute,
                                    second=self._earliest.second, microsecond=self._earliest.microsecond)
            earliest = earliest.in_timezone(UTC)
            if next_run < earliest:
                next_run = earliest

        if self._latest is not None:
            latest = next_run.in_timezone(local_tz)
            latest = latest.set(hour=self._latest.hour, minute=self._latest.minute,
                                second=self._latest.second, microsecond=self._latest.microsecond)
            latest = latest.in_timezone(UTC)
            if next_run > latest:
                next_run = latest

        self._set_next_run(next_run.timestamp())
        return next_run

    def _initialize_base_time(self, base_time: Union[None, int, float, timedelta, time, datetime],
                              now: Optional[DateTime] = None) -> DateTime:
        assert now is None or now.timezone is local_tz, now.timezone

        # since this is specified by the user its in the local timezone
        now = get_now(tz=local_tz) if now is None else now
        new_base: DateTime

        if base_time is None:
            # If we don't specify a datetime we start it now
            new_base = now.add(microseconds=1)
        elif isinstance(base_time, timedelta):
            # if it is a timedelta add it to now to easily specify points in the future
            new_base = now + base_time
        elif isinstance(base_time, (int, float)):
            new_base = now + timedelta(seconds=base_time)
        elif isinstance(base_time, time):
            # if it is a time object it specifies a time of day.
            new_base = now.set(hour=base_time.hour, minute=base_time.minute,
                               second=base_time.second, microsecond=base_time.microsecond)
            if new_base < now:
                new_base = new_base.add(days=1)
        else:
            assert isinstance(base_time, datetime)
            new_base = instance(base_time, tz=local_tz).astimezone(local_tz)

        assert isinstance(new_base, DateTime), type(new_base)
        if new_base <= now:
            raise FirstRunInThePastError(f'First run must be in the future! Now: {now}, run: {new_base}')

        new_base = new_base.in_timezone(UTC)
        self._next_base = new_base.timestamp()
        return new_base
