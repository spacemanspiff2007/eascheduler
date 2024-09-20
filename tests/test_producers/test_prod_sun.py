from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from whenever import Instant, ZonedDateTime

from eascheduler import get_sun_position
from eascheduler.producers import (
    DayOfWeekProducerFilter,
    DuskProducer,
    SunAzimuthProducer,
    SunElevationProducer,
    SunriseProducer,
    SunsetProducer,
)
from eascheduler.producers import prod_sun as prod_sun_module
from eascheduler.producers.prod_sun import SunProducer, get_azimuth_and_elevation
from tests.helper import get_ger_str, get_german_as_instant, get_system_as_instant


if TYPE_CHECKING:
    from collections.abc import Generator

    from _pytest.mark import ParameterSet


tz = 'Europe/Berlin'


@pytest.fixture(autouse=True)
def _setup():
    prod_sun_module.set_location(52.51870523376821, 13.376072914752532)

    yield

    # remove location
    assert hasattr(prod_sun_module, 'OBSERVER')
    prod_sun_module.OBSERVER = None


def get_params() -> Generator[ParameterSet, None, None]:
    # Double check with http://suncalc.net/#/52.5245,13.3717,17/2024.03.29/07:29
    # and for azimuth / elevation https://gml.noaa.gov/grad/solcalc/

    yield pytest.param(
        SunriseProducer(), get_system_as_instant(3, 29, 12, year=2024), '2024-03-30T05:44:59+01:00',
        id='Sunrise-30'
    )
    # DST change is on 2024-03-31 02:00
    yield pytest.param(
        SunriseProducer(), get_system_as_instant(3, 30, 12, year=2024), '2024-03-31T06:42:38+02:00',
        id='Sunrise-31'
    )

    yield pytest.param(
        SunsetProducer(), get_system_as_instant(3, 30, 12, year=2024), '2024-03-30T18:37:43+01:00',
        id='Sunset-30'
    )
    yield pytest.param(
        SunsetProducer(), get_system_as_instant(3, 31, 12, year=2024), '2024-03-31T19:39:28+02:00',
        id='Sunset-31'
    )
    yield pytest.param(
        DuskProducer(), get_system_as_instant(5, 15, 12, year=2024), '2024-05-15T21:40:46+02:00',
        id='Dusk-15',
    )
    yield pytest.param(
        SunElevationProducer(-6, 'setting'), get_german_as_instant(5, 15, 12, year=2024), '2024-05-15T21:40:46+02:00',
        id='Elevation-15',
    )
    yield pytest.param(
        SunAzimuthProducer(269.73), get_german_as_instant(5, 15, 1, year=2024), '2024-05-15T18:00:00+02:00',
        id='Azimuth-15-high',
    )
    yield pytest.param(
        SunAzimuthProducer(28.49), get_german_as_instant(5, 15, 1, year=2024), '2024-05-15T02:59:59+02:00',
        id='Azimuth-15-low',
    )


@pytest.mark.parametrize(('producer', 'dt', 'result'), get_params())
def test_sun(producer: SunProducer, dt: Instant, result: str):
    for _ in range(50):
        assert get_ger_str(producer.get_next(dt)) == result


def test_no_sun_pos():
    # http://suncalc.net/#/69.6529,18.9565,10/2024.05.16/13:11
    prod_sun_module.set_location(69.6529, 18.9565, 10)
    tz = 'Europe/Oslo'
    producer = SunriseProducer()

    dt = ZonedDateTime(2024, 5, 17, tz=tz)
    result = ZonedDateTime(2024, 5, 17, 0, 57, 52, tz=tz)

    assert producer.get_next(dt.instant()).to_tz(tz) == result
    # We don't have a sunrise, so we check that we jump forward
    assert producer.get_next(result.instant()).to_tz(tz) == ZonedDateTime(2024, 7, 27, 1, 30, 56, tz=tz)


def test_filter():
    dt = ZonedDateTime(2001, 1, 1, tz=tz)
    producer = SunriseProducer()

    for _ in range(10):
        assert producer.get_next(dt.instant()).to_tz(tz) == ZonedDateTime(2001, 1, 1, 8, 17, 43, tz=tz)

    producer._filter = DayOfWeekProducerFilter([6])

    for _ in range(10):
        assert producer.get_next(dt.instant()).to_tz(tz) == ZonedDateTime(2001, 1, 6, 8, 16, 20, tz=tz)


def test_sun_cache_eviction():

    producer = SunriseProducer()
    max_entries = 0

    for month in (5, 6):
        for day in range(1, 30):

            dt = ZonedDateTime(2024, month, day, tz=tz)
            producer.get_next(dt.instant()).to_tz(tz)
            max_entries = max(max_entries, len(prod_sun_module.SUN_CACHE))

    assert max_entries > len(prod_sun_module.SUN_CACHE) + 3


def test_sun_pos_calc():
    i = get_german_as_instant(5, 15, 12, year=2024)
    result = (153.94, 54.35)

    # actual implementation
    assert get_azimuth_and_elevation(i) == result

    # User facing function
    assert get_sun_position(i.py_datetime()) == result
