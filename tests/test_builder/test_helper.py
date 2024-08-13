from __future__ import annotations

import re
from datetime import time as dt_time
from datetime import timedelta as dt_timedelta

import pytest
from whenever import Instant, SystemDateTime, Time, TimeDelta, patch_current_time

from eascheduler.builder.helper import (
    BuilderTypeValidator,
    get_days,
    get_instant,
    get_months,
    get_pos_timedelta_secs,
    get_time,
    get_timedelta,
    get_weekdays,
)


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


def test_get_weekdays():
    assert get_weekdays(1) == [1]
    assert get_weekdays('Mo') == [1]
    assert get_weekdays('1') == [1]

    assert get_weekdays(1, 2) == [1, 2]
    assert get_weekdays('Mo', 2) == [1, 2]
    assert get_weekdays('Mo', 'Di') == [1, 2]

    assert get_weekdays('Mo-Mi', 'Fr-So') == [1, 2, 3, 5, 6, 7]
    assert get_weekdays('Mo-Mi,Fr-So') == [1, 2, 3, 5, 6, 7]
    assert get_weekdays('Mo-Mi', 1, 2) == [1, 2, 3]

    assert get_weekdays('Mo-Mo') == [1]
    assert get_weekdays('Di-Mo') == [1, 2, 3, 4, 5, 6, 7]
    assert get_weekdays('Sa-Mo') == [1, 6, 7]

    assert get_weekdays('1') == [1]
    assert get_weekdays('7') == [7]
    with pytest.raises(ValueError, match='Value 0 is not in the range 1-7'):
        get_weekdays('0')
    with pytest.raises(ValueError, match='Value 8 is not in the range 1-7'):
        get_weekdays('8')
    assert get_weekdays('1-3') == [1, 2, 3]
    assert get_weekdays('5-3') == [1, 2, 3, 5, 6, 7]


def test_get_days():
    assert get_days(1) == [1]
    assert get_days('1') == [1]
    assert get_days('1, 2, 3') == [1, 2, 3]

    assert get_days('1') == [1]
    assert get_days('31') == [31]
    with pytest.raises(ValueError, match='Value 0 is not in the range 1-31'):
        get_days('0')
    with pytest.raises(ValueError, match='Value 32 is not in the range 1-31'):
        get_days('32')

    assert get_days('1-3') == [1, 2, 3]
    assert get_days('1-3, 10-12') == [1, 2, 3, 10, 11, 12]
    assert get_days('30-3') == [1, 2, 3, 30, 31]


def test_get_months():
    assert get_months(1) == [1]
    assert get_months('January') == [1]

    assert get_months(1, 2) == [1, 2]
    assert get_months('January', 2) == [1, 2]
    assert get_months('January', 'February') == [1, 2]

    assert get_months('January-March', 'October-Dezember') == [1, 2, 3, 10, 11, 12]
    assert get_months('January-March,October-Dezember') == [1, 2, 3, 10, 11, 12]
    assert get_months('January-March', 1, 2) == [1, 2, 3]

    assert get_months('January-January') == [1]
    assert get_months('October-March') == [1, 2, 3, 10, 11, 12]

    assert get_months('1') == [1]
    assert get_months('12') == [12]
    with pytest.raises(ValueError, match='Value 0 is not in the range 1-12'):
        get_months('0')
    with pytest.raises(ValueError, match='Value 13 is not in the range 1-12'):
        get_months('13')


def test_builder_type_validator():
    class TestObj:
        def __init__(self, val):
            self.val = val

    v = BuilderTypeValidator(TestObj, int, 'val')

    assert str(v) == 'BuilderTypeValidator(TestObj, int, val)'

    with pytest.raises(TypeError, match=re.escape('Expected type TestObj, got 1 (int)')):
        v(1)

    with pytest.raises(TypeError, match=re.escape('Expected an instance of int, got asdf (str)')):
        v(TestObj('asdf'))

    assert v(TestObj(1)) == 1
