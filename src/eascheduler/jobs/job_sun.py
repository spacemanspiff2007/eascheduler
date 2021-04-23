from __future__ import annotations

from datetime import timedelta, datetime, time as dt_time
from typing import Optional, Union

from astral import Observer, sun  # type: ignore
from pendulum import DateTime, UTC
from pendulum import instance as pd_instance
from pendulum import now as get_now

from eascheduler.executors import ExecutorBase
from eascheduler.jobs.job_base_datetime import DateTimeJobBase
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

    def _schedule_first_run(self, first_run: Union[None, int, float, timedelta, dt_time, datetime]):
        raise NotImplementedError()

    def _advance_time(self, utc_dt: DateTime) -> DateTime:
        return pd_instance(self._sun_func(OBSERVER, utc_dt.add(days=1).date(), tzinfo=UTC)).set(microsecond=0)

    def _schedule_next_run(self):
        dt_next = get_now(UTC)
        next_run = pd_instance(self._sun_func(OBSERVER, dt_next.date(), tzinfo=UTC)).set(microsecond=0)

        while next_run <= get_now(UTC):
            next_run = self._advance_time(next_run)

        self._next_run_base = next_run.timestamp()
        self._apply_boundaries()


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
