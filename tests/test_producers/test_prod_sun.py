from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from whenever import Instant, ZonedDateTime

from eascheduler.producers import DayOfWeekProducerFilter
from eascheduler.producers import prod_sun as prod_sun_module
from eascheduler.producers.prod_sun import SunProducer, SunriseProducer, SunsetProducer
from tests.helper import get_ger_str, get_system_as_instant


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

    yield pytest.param(
        SunriseProducer(), get_system_as_instant(3, 29, 12, year=2024), '2024-03-30T05:44:58+01:00',
        id='Sunrise-30'
    )
    # DST change is on 2024-03-31 02:00
    yield pytest.param(
        SunriseProducer(), get_system_as_instant(3, 30, 12, year=2024), '2024-03-31T06:42:37+02:00',
        id='Sunrise-31'
    )

    yield pytest.param(
        SunsetProducer(), get_system_as_instant(3, 30, 12, year=2024), '2024-03-30T18:37:42+01:00',
        id='Sunset-30'
    )
    yield pytest.param(
        SunsetProducer(), get_system_as_instant(3, 31, 12, year=2024), '2024-03-31T19:39:27+02:00',
        id='Sunset-31'
    )


@pytest.mark.parametrize(('producer', 'dt', 'result'), get_params())
def test_sun(producer: SunProducer, dt: Instant, result: str):
    for _ in range(10):
        assert get_ger_str(producer.get_next(dt)) == result


def test_no_sun_pos():
    # http://suncalc.net/#/69.6529,18.9565,10/2024.05.16/13:11
    prod_sun_module.set_location(69.6529, 18.9565, 10)
    tz = 'Europe/Oslo'
    producer = SunriseProducer()

    dt = ZonedDateTime(2024, 5, 17, tz=tz)
    result = ZonedDateTime(2024, 5, 17, 0, 57, 51, tz=tz)

    assert producer.get_next(dt.instant()).to_tz(tz) == result
    # We don't have a sunrise, so we check that we jump forward
    assert producer.get_next(result.instant()).to_tz(tz) == ZonedDateTime(2024, 7, 27, 1, 30, 55, tz=tz)


def test_filter():
    dt = ZonedDateTime(2001, 1, 1, tz=tz)
    producer = SunriseProducer()

    for _ in range(10):
        assert producer.get_next(dt.instant()).to_tz(tz) == ZonedDateTime(2001, 1, 1, 8, 17, 42, tz=tz)

    producer._filter = DayOfWeekProducerFilter([6])

    for _ in range(10):
        assert producer.get_next(dt.instant()).to_tz(tz) == ZonedDateTime(2001, 1, 6, 8, 16, 19, tz=tz)
