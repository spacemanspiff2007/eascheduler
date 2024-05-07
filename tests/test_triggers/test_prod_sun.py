from collections.abc import Generator

import pytest
from _pytest.mark import ParameterSet
from pendulum import DateTime, Timezone

from eascheduler.triggers import prod_sun as prod_sun_module
from eascheduler.triggers.prod_sun import SunProducer, SunriseProducer, SunsetProducer


tz = Timezone('Europe/Berlin')


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
        SunriseProducer, DateTime(2024, 3, 29, 12, tzinfo=tz), DateTime(2024, 3, 30, 5, 44, 58, tzinfo=tz),
        id='Sunrise-30'
    )
    # DST change is on 2024-03-31 02:00
    yield pytest.param(
        SunriseProducer, DateTime(2024, 3, 30, 12, tzinfo=tz), DateTime(2024, 3, 31, 6, 42, 37, tzinfo=tz),
        id='Sunrise-31'
    )

    yield pytest.param(
        SunsetProducer, DateTime(2024, 3, 29, 19, tzinfo=tz), DateTime(2024, 3, 30, 18, 37, 42, tzinfo=tz),
        id='Sunset-30'
    )


@pytest.mark.parametrize(('producer', 'dt', 'result'), get_params())
def test_sun(producer: SunProducer, dt: DateTime, result: DateTime):
    assert producer.get_next(dt) == result


def test_no_sun_pos():
    prod_sun_module.set_location(69.6529, 18.9565, 10)
    tz = Timezone('Europe/Oslo')

    dt = DateTime(2024, 5, 16, tzinfo=tz)
    result = DateTime(2024, 5, 16, 1, 19, 58, tzinfo=tz)
    assert SunriseProducer.get_next(dt) == result

    # We don't have a sunrise, so we check that we jump forward
    assert SunriseProducer.get_next(result) == DateTime(2024, 7, 27, 1, 30, 55, tzinfo=tz)
