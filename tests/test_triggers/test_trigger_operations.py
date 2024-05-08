from datetime import datetime
from datetime import time as dt_dtime

from pendulum import DateTime, Timezone

import eascheduler.triggers.trigger_operations as operations_module
from eascheduler.triggers import (
    EarliestDateTimeOperation,
    FunctionDateTimeOperation,
    JitterDateTimeOperation,
    LatestDateTimeOperation,
    OffsetDateTimeOperation,
)


def dt(day, hour, minute=0):
    return DateTime(2001, 1, day, hour, minute=minute, tzinfo=Timezone('Europe/Berlin'))


def test_index():
    classes = [getattr(operations_module, name) for name in dir(operations_module) if name.endswith('Operation')]
    for cls in classes:
        assert cls in operations_module.SORT_ORDER


def test_offset():
    o = OffsetDateTimeOperation(5)
    assert o == OffsetDateTimeOperation(5)
    assert o.apply(dt(1, 12)) == dt(1, 12).add(seconds=5)

    o = OffsetDateTimeOperation(-5)
    assert o.apply(dt(1, 12)) == dt(1, 12).subtract(seconds=5)


def test_jitter():
    j = JitterDateTimeOperation(30)
    assert j == JitterDateTimeOperation(30)

    dt_obj = dt(1, 12)
    for _ in range(100):
        assert dt_obj <= j.apply(dt_obj) <= dt_obj.add(seconds=30)

    j = JitterDateTimeOperation(-30, 30)
    for _ in range(100):
        assert dt_obj.subtract(seconds=30) <= j.apply(dt_obj) <= dt_obj.add(seconds=30)


def test_latest():
    o = LatestDateTimeOperation(dt_dtime(12, 30))
    assert o == LatestDateTimeOperation(dt_dtime(12, 30))

    assert o.apply(dt(1, 12)) == dt(1, 12)
    assert o.apply(dt(1, 12, 30)) == dt(1, 12, 30)
    assert o.apply(dt(1, 12, 31)) == dt(1, 12, 30)


def test_earliest():
    o = EarliestDateTimeOperation(dt_dtime(12, 30))
    assert o == EarliestDateTimeOperation(dt_dtime(12, 30))

    assert o.apply(dt(1, 12, 29)) == dt(1, 12, 30)
    assert o.apply(dt(1, 12, 30)) == dt(1, 12, 30)
    assert o.apply(dt(1, 12, 35)) == dt(1, 12, 35)


def test_function():

    def my_func(d: datetime):
        return d.replace(minute=15)

    o = FunctionDateTimeOperation(my_func)
    assert o == FunctionDateTimeOperation(my_func)

    assert o.apply(dt(1, 12)) == dt(1, 12, 15)
