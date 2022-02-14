from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from typing import Optional, TYPE_CHECKING, Union

from pendulum import DateTime, from_timestamp, instance
from pendulum import now as get_now
from pendulum import UTC

from eascheduler.const import FAR_FUTURE, local_tz
from eascheduler.errors import FirstRunInThePastError, JobAlreadyCanceledException
from eascheduler.executors import ExecutorBase

if TYPE_CHECKING:
    from eascheduler.schedulers import AsyncScheduler


class ScheduledJobBase:
    def __init__(self, parent: 'AsyncScheduler', func: ExecutorBase):
        self._func: ExecutorBase = func

        # time when we run as a UTC timestamp
        self._next_run: float = FAR_FUTURE

        # If parent is set it's also the indication that the job is scheduled
        self._parent: Optional['AsyncScheduler'] = parent

    def _execute(self):
        self._schedule_next_run()
        self._func.execute()

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        raise NotImplementedError()

    def _schedule_next_run(self):
        raise NotImplementedError()

    def _set_next_run(self, next_run: float):
        assert isinstance(next_run, (float, int))
        if self._parent is None:
            raise JobAlreadyCanceledException()

        next_run = round(next_run, 3)   # ms accuracy is enough
        if self._next_run == next_run:  # only set and subsequently reschedule if the timestamp changed
            return None

        self._next_run = next_run
        self._parent.add_job(self)

    def cancel(self):
        """Cancel the job."""
        if self._parent is None:
            raise JobAlreadyCanceledException()

        # Indicate that the job is canceled
        self._next_run = FAR_FUTURE

        # remove only once from parent!
        parent = self._parent
        self._parent = None
        parent.remove_job(self)

    def get_next_run(self) -> datetime:
        """Return the next execution timestamp."""
        return from_timestamp(self._next_run, local_tz).naive()

    def remaining(self) -> Optional[timedelta]:
        """Returns the remaining time to the next run or None if the job is not scheduled

        :return: remaining time as a timedelta or None
        """
        if self._next_run >= FAR_FUTURE:
            return None
        return timedelta(seconds=self._next_run - get_now(UTC).timestamp())

    def __lt__(self, other):
        """Instances of ScheduledJobBase are sortable based on the scheduled time they run next."""
        return self._next_run < other._next_run

    def __repr__(self):
        return f'<{self.__class__.__name__} next_run: {self.get_next_run()}>'


def get_first_timestamp(base_time: Union[None, int, float, timedelta, dt_time, datetime]) -> float:

    # since this is specified by the user its in the local timezone
    now = get_now(tz=local_tz)
    new_base: DateTime

    if base_time is None:
        # If we don't specify a datetime we start it now
        new_base = now
    elif isinstance(base_time, timedelta):
        # if it is a timedelta add it to now to easily specify points in the future
        new_base = now + base_time
    elif isinstance(base_time, (int, float)):
        new_base = now + timedelta(seconds=base_time)
    elif isinstance(base_time, dt_time):
        # if it is a time object it specifies a time of day.
        new_base = now.set(hour=base_time.hour, minute=base_time.minute,
                           second=base_time.second, microsecond=base_time.microsecond)
        if new_base < now:
            new_base = new_base.add(days=1)
    else:
        assert isinstance(base_time, datetime)
        new_base = instance(base_time, tz=local_tz).astimezone(local_tz)

    assert isinstance(new_base, DateTime), type(new_base)
    if new_base < now:
        raise FirstRunInThePastError(f'First run can not be in the past! Now: {now}, run: {new_base}')

    return new_base.timestamp()
