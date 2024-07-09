from __future__ import annotations

from typing import TYPE_CHECKING, Final

from astral import Observer, sun
from typing_extensions import override
from whenever import Instant

from eascheduler.errors.errors import LocationNotSetError
from eascheduler.producers.base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date as dt_date
    from datetime import datetime


OBSERVER: Observer | None = None


def set_location(latitude: float, longitude: float, elevation: float = 0.0) -> None:
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

    if not isinstance(latitude, (int, float, str)):
        msg = f'latitude must be float or str, not {type(latitude)}'
        raise TypeError(msg)

    if not isinstance(longitude, (int, float, str)):
        msg = f'longitude must be float or str, not {type(longitude)}'
        raise TypeError(msg)

    if not isinstance(elevation, (int, float, tuple)):
        msg = f'elevation must be float or tuple of floats, not {type(elevation)}'
        raise TypeError(msg)

    OBSERVER = Observer(latitude, longitude, float(elevation))


class SunProducer(DateTimeProducerBase):
    __slots__ = ('func', )

    def __init__(self, func: Callable[[Observer, dt_date], datetime]) -> None:
        super().__init__()

        self.func: Final = func

    @override
    def get_next(self, dt: Instant) -> Instant:   # type: ignore[return]

        new_dt = dt
        if (observer := OBSERVER) is None:
            raise LocationNotSetError()

        for _ in not_infinite_loop():  # noqa: RET503

            # If we are very far north or very far south it's possible that we don't have a sunrise at all
            # If that's the case we advance and schedule for the next date that actually has a sunrise
            next_sun = None  # type: datetime | None
            while next_sun is None:
                try:
                    next_sun = self.func(observer, new_dt.to_tz('UTC').date().py_date())
                except ValueError:  # noqa: PERF203
                    new_dt = new_dt.add(hours=24)

            # Date has to be in the future
            new_dt = Instant.from_py_datetime(next_sun.replace(microsecond=0))
            if new_dt > dt and ((f := self._filter) is None or f.allow(new_dt.to_system_tz())):
                return new_dt

            new_dt = new_dt.add(hours=24)


class DawnProducer(SunProducer):
    def __init__(self) -> None:
        super().__init__(sun.dawn)


class SunriseProducer(SunProducer):
    def __init__(self) -> None:
        super().__init__(sun.sunrise)


class NoonProducer(SunProducer):
    def __init__(self) -> None:
        super().__init__(sun.noon)


class SunsetProducer(SunProducer):
    def __init__(self) -> None:
        super().__init__(sun.sunset)


class DuskProducer(SunProducer):
    def __init__(self) -> None:
        super().__init__(sun.dusk)
