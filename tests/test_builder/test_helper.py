from __future__ import annotations

from datetime import time as dt_time
from datetime import timedelta as dt_timedelta

import pytest
from whenever import Instant, SystemDateTime, Time, TimeDelta, patch_current_time

from eascheduler.builder.helper import get_instant, get_pos_timedelta_secs, get_time, get_timedelta


def test_get_timedelta():
    assert get_timedelta(dt_timedelta(seconds=3.5)) == TimeDelta(seconds=3.5)
    assert get_timedelta(TimeDelta(seconds=3.7)) == TimeDelta(seconds=3.7)
    assert get_timedelta(3.5) == TimeDelta(seconds=3.5)
    assert get_timedelta(3) == TimeDelta(seconds=3)
    assert get_timedelta('PT1H30M') == TimeDelta(hours=1, minutes=30)

    assert get_pos_timedelta_secs(dt_timedelta(seconds=3.5)) == 3.5
    with pytest.raises(ValueError):  # noqa: PT011
        get_pos_timedelta_secs(dt_timedelta(seconds=-3.5))


def test_get_time():
    assert get_time(dt_time(12, 34, 56)) == Time(12, 34, 56)
    assert get_time(Time(12, 34, 56)) == Time(12, 34, 56)
    assert get_time('12:34:56') == Time(12, 34, 56)


def test_get_instant():
    i = Instant.from_utc(2001, 1, 1)

    with patch_current_time(i, keep_ticking=False):
        # Immediately
        assert get_instant(None) == i
        # Timedelta test
        assert get_instant(3600) == i.add(hours=1)
        # Time test
        assert get_instant('08:00:00') == SystemDateTime(2001, 1, 1, 8).instant()
