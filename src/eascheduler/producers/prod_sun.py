from __future__ import annotations

from collections import OrderedDict
from datetime import datetime as dt_datetime
from datetime import timedelta as dt_timedelta
from datetime import timezone as dt_timezone
from typing import TYPE_CHECKING, Final, Literal

from astral import Observer, SunDirection, sun
from typing_extensions import override
from whenever import Instant

from eascheduler.errors.errors import LocationNotSetError
from eascheduler.producers.base import DateTimeProducerBase, not_infinite_loop


if TYPE_CHECKING:
    from collections.abc import Callable, Hashable
    from datetime import date as dt_date
    from datetime import datetime


OBSERVER: Observer | None = None


def set_location(latitude: float | str, longitude: float | str, elevation: float | tuple[float, float] = 0.0) -> None:
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

    OBSERVER = Observer(latitude, longitude, elevation)


SUN_CACHE: Final = OrderedDict()


class SunProducer(DateTimeProducerBase):
    __slots__ = ('func', )

    def __init__(self, func: Callable[[Observer, dt_date], datetime]) -> None:
        super().__init__()

        self.func: Final = func

    def _cache_key(self) -> tuple[Hashable, ...]:
        return (self.__class__, )

    def _get_next_sun(self, dt: Instant) -> Instant:
        if (observer := OBSERVER) is None:
            raise LocationNotSetError()

        sun_cache = SUN_CACHE

        # we cache the SUN calculations because they are somewhat expensive
        key = (dt.to_tz('UTC').date(), id(observer)) + self._cache_key()
        if (obj := sun_cache.get(key)) is not None:
            sun_cache.move_to_end(key)
            return obj

        # If we are very far north or very far south it's possible that we don't have a sunrise at all
        # If that's the case we advance and schedule for the next date that actually has a sunrise
        tries = 366
        for i in range(tries + 1):
            try:
                next_sun = self.func(observer, dt.to_tz('UTC').date().py_date())
            except ValueError:  # noqa: PERF203
                dt = dt.add(hours=24)
                if i >= tries:
                    raise
            else:
                break
        else:
            raise RuntimeError()

        # round to next full second if necessary
        if next_sun.microsecond:
            instant = Instant.from_py_datetime(next_sun.replace(microsecond=0)).add(seconds=1)
        else:
            instant = Instant.from_py_datetime(next_sun)

        # limit cache size
        if len(sun_cache) >= 64:
            for _ in range(10):
                sun_cache.popitem(last=False)

        sun_cache[key] = instant
        return instant

    @override
    def get_next(self, dt: Instant) -> Instant:   # type: ignore[return]

        new_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503

            # Date has to be in the future
            new_dt = self._get_next_sun(new_dt)
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


class SunElevationProducer(SunProducer):
    def __init__(self, elevation: float, direction: Literal['rising', 'setting']) -> None:
        if elevation < -90 or elevation > 90:
            msg = 'Elevation must be between -90 and 90'
            raise ValueError(msg)

        self.elevation: Final = elevation
        self.direction: Final = {'rising': SunDirection.RISING, 'setting': SunDirection.SETTING}[direction]
        super().__init__(self._sun_func)

    def _sun_func(self, observer: Observer, date: dt_date) -> datetime:
        return sun.time_at_elevation(observer, self.elevation, date, self.direction)

    @override
    def _cache_key(self) -> tuple[Hashable, ...]:
        return self.__class__, self.elevation, self.direction


class SunAzimuthProducer(SunProducer):
    def __init__(self, azimuth: float) -> None:
        if not 0 <= azimuth <= 360:
            msg = 'Azimuth must be between 0° and 360°'
            raise ValueError(msg)

        self.azimuth: Final = azimuth
        super().__init__(self._sun_func)

    @override
    def _cache_key(self) -> tuple[Hashable, ...]:
        return self.__class__, self.azimuth

    def _sun_func(self, observer: Observer, date: dt_date) -> datetime:
        # I'm not smart enough to implement the azimuth calculation myself,
        # so I'm using this hack to get the time of day when the azimuth is the closest to the target

        sec_per_az = 86400 / 360
        az_target = self.azimuth

        dt = dt_datetime(date.year, date.month, date.day, 12, 0, 0, tzinfo=dt_timezone.utc)

        while not_infinite_loop():
            az = sun.azimuth(observer, dt)
            az_diff = abs(az_target - az)
            sign = 1 if az_target > az else -1

            if az_diff < 0.01 and sign == -1:
                break

            secs_diff = round(az_diff * sec_per_az)
            if not secs_diff:
                secs_diff = 1
            dt = dt + dt_timedelta(seconds=sign * secs_diff)

        return dt


def get_azimuth_and_elevation(instant: Instant) -> tuple[float, float]:
    if (observer := OBSERVER) is None:
        raise LocationNotSetError()

    zenith, azimuth = sun.zenith_and_azimuth(observer, instant.to_tz('UTC').py_datetime())

    return round(azimuth, 2), round(90 - zenith, 2)
