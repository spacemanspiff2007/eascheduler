from __future__ import annotations

from datetime import date, datetime
from datetime import time as dt_time
from typing import Union, Set, Iterable, Optional, Dict

from pendulum import DateTime, from_timestamp, UTC
from pendulum import now as get_now

from eascheduler.const import SKIP_EXECUTION, local_tz
from eascheduler.errors import UnknownWeekdayError, JobAlreadyCanceledException
from eascheduler.executors.executor import ExecutorBase
from eascheduler.schedulers import AsyncScheduler
from .job_datetime_base import DateTimeJobBase

# names of weekdays in local language
day_names: Dict[str, int] = {date(2001, 1, i).strftime('%A'): i for i in range(1, 8)}
day_names.update({date(2001, 1, i).strftime('%A')[:3]: i for i in range(1, 8)})

# abbreviations in German and English
day_names.update({"Mo": 1, "Di": 2, "Mi": 3, "Do": 4, "Fr": 5, "Sa": 6, "So": 7})
day_names.update({"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7})
day_names = {k.lower(): v for k, v in day_names.items()}


class DayOfWeekJob(DateTimeJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func)
        self._time: dt_time = dt_time(hour=12)
        self._weekdays: Set[int] = {1, 2, 3, 4, 5, 6, 7}

    def _update_run_time(self, next_run: Optional[DateTime] = None) -> DateTime:
        update_run_time = super()._update_run_time
        # Starting point is always the next call from UTC
        if next_run is None:
            next_run = from_timestamp(self._next_base)

        # Allow skipping certain occurrences
        res = update_run_time(next_run)
        while res is SKIP_EXECUTION:
            # The day check has to be in the local timezone
            next_run = next_run.in_timezone(local_tz)
            next_run = next_run.add(days=1)

            while not next_run.isoweekday() in self._weekdays:
                next_run = next_run.add(days=1)
            next_run = next_run.in_timezone(UTC)

            res = update_run_time(next_run)
        return next_run

    def _update_base_time(self):
        now = get_now(tz=local_tz)
        next_run = now.set(hour=self._time.hour, minute=self._time.minute,
                           second=self._time.second, microsecond=self._time.microsecond)
        while next_run < now:
            next_run = next_run.add(days=1)

        while next_run.isoweekday() not in self._weekdays:
            next_run = next_run.add(days=1)

        next_run = next_run.in_timezone(UTC)
        self._next_base = next_run.timestamp()
        self._update_run_time(next_run)
        return self

    def time(self, time: Union[dt_time, datetime]) -> DayOfWeekJob:
        """Set a time of day when the job will run.

        :param time: time
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        self._time = time if isinstance(time, dt_time) else time.time()

        self._update_base_time()
        return self

    def weekdays(self, weekdays: Union[str, Iterable[Union[str, int]]]) -> DayOfWeekJob:
        """Set the weekdays when the job will run.

        :param weekdays: Day group names  (e.g. ``'all'``, ``'weekend'``, ``'workdays'``), an iterable with
                         day names (e.g. ``['Mon', 'Fri']``) or an iterable with the isoweekday values
                         (e.g. ``[1, 5]``).
        """
        if self._parent is None:
            raise JobAlreadyCanceledException()

        int_days: Set[int] = set()
        try:
            if isinstance(weekdays, str):
                weekdays = weekdays.lower()
                if weekdays == 'weekend':
                    int_days = {6, 7}
                elif weekdays == 'workdays':
                    int_days = {1, 2, 3, 4, 5}
                elif weekdays == 'all' or weekdays == 'every day':
                    int_days = {1, 2, 3, 4, 5, 6, 7}
                else:
                    int_days = {day_names[weekdays]}
            else:
                for k in weekdays:
                    int_days.add(day_names[k.lower()] if isinstance(k, str) else k)
        except KeyError as e:
            raise UnknownWeekdayError(f'Unknown day "{e.args[0]}"! Available: {", ".join(day_names)}') from None

        for k in int_days:
            assert 1 <= k <= 7, k
        self._weekdays = int_days

        self._update_base_time()
        return self
