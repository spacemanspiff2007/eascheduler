from __future__ import annotations

from datetime import datetime, timedelta
from typing import Final

from astral import Observer, sun
from pendulum import DateTime
from pendulum import instance as pd_instance

from .base import DateTimeProducerBase, not_infinite_loop


OBSERVER: Observer | None = None


def set_location(latitude: float, longitude: float, elevation: float | int = 0.0):
    """
        Latitude and longitude can be set either as a float or as a string.
    For strings they must be of the form

        degrees°minutes'seconds"[N|S|E|W] e.g. 51°31'N

    `minutes` & `seconds` are optional.


    :param latitude: Latitude - Northern latitudes should be positive (e.g. 52.5185537)
    :param longitude: Longitude - Eastern longitudes should be positive (e.g. 13.3758636)
    :param elevation: Elevation above sea level (e.g. 43.0)
    :return:
    """
    global OBSERVER

    assert isinstance(latitude, (float, str)), type(latitude)
    assert isinstance(longitude, (float, str)), type(longitude)
    OBSERVER = Observer(latitude, longitude, float(elevation))


class SunProducer(DateTimeProducerBase):
    def __init__(self, func):
        self.func: Final = func

    def get_next(self, now: DateTime, dt: DateTime) -> DateTime:

        while not_infinite_loop():  # noqa: RET503

            # If we are very far north or very far south it's possible that we don't have a sunrise at all
            # If that's the case we advance and schedule for the next date that actually has a sunrise
            next_sun = None  # type: datetime | None
            while next_sun is None:
                try:
                    next_sun = self.func(OBSERVER, dt.date(), tzinfo=dt.tzinfo)
                except ValueError:  # noqa: PERF203
                    dt += timedelta(days=1)

            # Date has to be in the future
            next_dt = pd_instance(next_sun, tz=dt.tz).set(microsecond=0)
            if next_dt > now:
                return next_dt

            dt += timedelta(days=1)


DawnProducer: Final = SunProducer(sun.dawn)
SunriseProducer: Final = SunProducer(sun.sunrise)
NoonProducer: Final = SunProducer(sun.noon)
SunsetProducer: Final = SunProducer(sun.sunset)
DuskProducer: Final = SunProducer(sun.dusk)