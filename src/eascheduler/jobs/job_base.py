from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pendulum import from_timestamp

from eascheduler.const import FAR_FUTURE, local_tz
from eascheduler.errors import JobAlreadyCanceledException
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

    def _set_next_run(self, next_run: float):
        assert isinstance(next_run, (float, int))

        next_run = round(next_run, 3)   # ms accuracy is enough
        if self._next_run == next_run:  # only set and subsequently reschedule if the timestamp changed
            return None

        self._next_run = next_run
        self._parent.add_job(self)

    def cancel(self):
        """Cancel the job."""
        if self._parent is None:
            raise JobAlreadyCanceledException()

        # remove only once!
        parent = self._parent
        self._parent = None
        parent.remove_job(self)

    def __lt__(self, other):
        """Instances of ScheduledJobBase are sortable based on the scheduled time they run next."""
        return self._next_run < other._next_run

    def __repr__(self):
        return f'<{self.__class__.__name__} next_run: {self.get_next_run()}>'

    def get_next_run(self) -> datetime:
        """Return the next execution timestamp."""
        return from_timestamp(self._next_run, local_tz).naive()
