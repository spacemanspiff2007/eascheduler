from __future__ import annotations

from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from random import uniform
from typing import Callable, Optional, Tuple, Union

from pendulum import DateTime, from_timestamp, instance
from pendulum import now as get_now
from pendulum import UTC

from eascheduler.const import FAR_FUTURE, local_tz, SKIP_EXECUTION
from eascheduler.errors import BoundaryFunctionError, JobAlreadyCanceledException
from eascheduler.executors.executor import ExecutorBase
from eascheduler.jobs.job_base import get_first_timestamp, ScheduledJobBase
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
        self._next_run_base: float = FAR_FUTURE
        self._last_run_base: float = 0

        # adjusting of the boundaries is running
        self._adjusting: bool = False

        # boundaries
        self._earliest: Optional[dt_time] = None
        self._latest: Optional[dt_time] = None
        self._offset: Optional[timedelta] = None
        self._jitter: Optional[Tuple[float, float]] = None
        self._boundary_func: Optional[Callable[[datetime], datetime]] = None

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        self._next_run_base = get_first_timestamp(first_run)
        self._set_next_run(self._next_run_base)

    def _advance_time(self, utc_dt: DateTime) -> DateTime:
        raise NotImplementedError()

    def _execute(self):
        self._last_run_base = self._next_run_base
        super()._execute()

    def earliest(self, time_obj: Optional[dt_time]) -> DateTimeJobBase:
        """Set earliest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run earlier
        """
        assert isinstance(time_obj, dt_time) or time_obj is None, type(time_obj)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._earliest != time_obj
        self._earliest = time_obj
        if changed and not self._adjusting:
            self._apply_boundaries()
        return self

    def latest(self, time_obj: Optional[dt_time]) -> DateTimeJobBase:
        """Set latest boundary as time of day. ``None`` will disable boundary.

        :param time_obj: time obj, scheduler will not run later
        """
        assert isinstance(time_obj, dt_time) or time_obj is None, type(time_obj)

        if self._parent is None:
            raise JobAlreadyCanceledException()

        changed = self._latest != time_obj
        self._latest = time_obj
        if changed and not self._adjusting:
            self._apply_boundaries()
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
        if changed and not self._adjusting:
            self._apply_boundaries()
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
        if changed and not self._adjusting:
            self._apply_boundaries()
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
            if self._adjusting:
                raise BoundaryFunctionError('Can not change the boundary function from inside the boundary function!')
            self._apply_boundaries()
        return self

    def _apply_boundaries(self):
        self._adjusting = True

        # Starting point is always the next call in local time
        next_run_local: DateTime = from_timestamp(self._next_run_base, local_tz)

        while True:
            # custom boundaries first
            if self._boundary_func is not None:
                naive_obj = next_run_local.in_timezone(local_tz).naive()
                custom_obj = self._boundary_func(naive_obj)
                if custom_obj is SKIP_EXECUTION:
                    next_run_local = self._advance_time(next_run_local.in_timezone(UTC)).in_timezone(local_tz)
                    continue
                next_run_local = instance(custom_obj, local_tz).astimezone(local_tz)

            if self._offset is not None:
                next_run_local += self._offset  # offset doesn't have to be localized

            if self._jitter is not None:
                next_run_local += timedelta(seconds=uniform(self._jitter[0], self._jitter[1]))

            if self._earliest is not None:
                earliest = next_run_local.set(hour=self._earliest.hour, minute=self._earliest.minute,
                                              second=self._earliest.second, microsecond=self._earliest.microsecond)
                if next_run_local < earliest:
                    next_run_local = earliest

            if self._latest is not None:
                latest = next_run_local.set(hour=self._latest.hour, minute=self._latest.minute,
                                            second=self._latest.second, microsecond=self._latest.microsecond)
                if next_run_local > latest:
                    next_run_local = latest

            # if we are in the future we have the next run
            next_run = next_run_local.in_timezone(UTC)
            if get_now(UTC) < next_run:
                break

            # Otherwise we advance a step in the future
            next_run_local = self._advance_time(next_run).in_timezone(local_tz)

        self._adjusting = False
        self._set_next_run(next_run.timestamp())
        return next_run_local
