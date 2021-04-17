from __future__ import annotations

from typing import Optional, Union

from astral import Observer, sun  # type: ignore
from pendulum import DateTime, from_timestamp, UTC
from pendulum import instance as pd_instance
from pendulum import now as get_now

from eascheduler.const import SKIP_EXECUTION
from eascheduler.executors import ExecutorBase
from eascheduler.jobs.job_datetime_base import DateTimeJobBase
from eascheduler.schedulers import AsyncScheduler

OBSERVER: Optional[Observer] = None


def set_location(latitude: float, longitude: float, elevation: Union[float, int] = 0.0):
    """
        Latitude and longitude can be set either as a float or as a string.
    For strings they must be of the form

        degrees°minutes'seconds"[N|S|E|W] e.g. 51°31'N

    `minutes’` & `seconds”` are optional.


    :param latitude: Latitude - Northern latitudes should be positive (e.g. 52.5185537)
    :param longitude: Longitude - Eastern longitudes should be positive (e.g. 13.3758636)
    :param elevation: Elevation above sea level (e.g. 43.0)
    :return:
    """
    global OBSERVER
    assert isinstance(latitude, (float, str)), type(latitude)
    assert isinstance(longitude, (float, str)), type(longitude)
    OBSERVER = Observer(latitude, longitude, float(elevation))


class SunJobBase(DateTimeJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase, sun_func):
        super().__init__(parent, func)
        self._sun_func = sun_func

    def _update_base_time(self):
        dt_next = get_now(UTC)
        next_run = pd_instance(self._sun_func(OBSERVER, dt_next.date(), tzinfo=UTC)).set(microsecond=0)

        while next_run <= get_now(UTC):
            dt_next = dt_next.add(days=1)
            next_run = pd_instance(self._sun_func(OBSERVER, dt_next.date(), tzinfo=UTC)).set(microsecond=0)

        self._next_base = next_run.timestamp()
        self._update_run_time(next_run)

    def _update_run_time(self, dt_start: Optional[DateTime] = None) -> DateTime:
        update_run_time = super()._update_run_time

        # initialize next run
        dt_next = from_timestamp(self._next_base) if dt_start is None else dt_start

        # Allow skipping certain occurrences
        next_run = update_run_time(dt_next)
        while next_run is SKIP_EXECUTION or next_run <= get_now(UTC):
            dt_next = dt_next.add(days=1)
            next_run = update_run_time(
                pd_instance(self._sun_func(OBSERVER, dt_next.date(), tzinfo=UTC)).set(microsecond=0)
            )

        return next_run


class SunriseJob(SunJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func, sun.sunrise)


class SunsetJob(SunJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func, sun.sunset)


class DuskJob(SunJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func, sun.dusk)


class DawnJob(SunJobBase):
    def __init__(self, parent: AsyncScheduler, func: ExecutorBase):
        super().__init__(parent, func, sun.dawn)
