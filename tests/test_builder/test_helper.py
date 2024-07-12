from __future__ import annotations

from datetime import time as dt_time
from datetime import timedelta as dt_timedelta

import pytest
from whenever import Time, TimeDelta

from eascheduler.builder.helper import get_int, get_time


def test_get_int():
    assert get_int(dt_timedelta(seconds=3.5)) == 3
    assert get_int(TimeDelta(seconds=3.5)) == 3
    assert get_int(3.5) == 3
    assert get_int(3) == 3


def test_get_time():
    assert get_time(dt_time(12, 34, 56)) == Time(12, 34, 56)
    assert get_time(Time(12, 34, 56)) == Time(12, 34, 56)
    assert get_time('12:34:56') == Time(12, 34, 56)


@pytest.mark.skip(reason='Mocking not implemented yet')
def test_get_instant():
    # TODO: Implement tests as soon as we can mock Instant.now()
    pass
