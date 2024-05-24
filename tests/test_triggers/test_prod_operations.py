from datetime import datetime
from datetime import time as dt_time
from unittest.mock import Mock

import pytest
from pendulum import DateTime, Timezone

import eascheduler.triggers.prod_operation as prod_operation_module
from eascheduler.triggers.prod_interval import IntervalProducer
from eascheduler.triggers.prod_operation import (
    EarliestProducerOperation,
    JitterProducerOperation,
    LatestProducerOperation,
    OffsetProducerOperation,
)


def dt(day, hour, minute=0, second=0):
    return DateTime(2001, 1, day, hour, minute=minute, second=second, tzinfo=Timezone('Europe/Berlin'))


class PatchedUniform:
    def __init__(self):
        self.ctr = 0

    def __call__(self, low, high):
        if self.ctr == 0:
            self.ctr += 1
            return low
        if self.ctr == 1:
            self.ctr += 1
            return (low + high) / 2
        if self.ctr == 2:
            self.ctr = 0
            return high

        raise ValueError()


@pytest.fixture(autouse=True)
def _patch_uniform(monkeypatch):
    monkeypatch.setattr(prod_operation_module, 'uniform', PatchedUniform())


def test_earliest():

    o = EarliestProducerOperation(IntervalProducer(dt(1, 0), 3600), dt_time(8, 0, 0))

    assert o.get_next(dt(1, 3)) == dt(1, 8)
    assert o.get_next(dt(1, 7, 1)) == dt(1, 8)
    assert o.get_next(dt(1, 22)) == dt(1, 23)
    assert o.get_next(dt(1, 23)) == dt(2, 8)


def test_latest():

    o = LatestProducerOperation(IntervalProducer(dt(1, 0, 30), 3600), dt_time(8, 0, 0))

    assert o.get_next(dt(1, 7)) == dt(1, 7, 30)
    assert o.get_next(dt(1, 7, 59)) == dt(1, 8)
    assert o.get_next(dt(1, 8, 1)) == dt(2, 0, 30)


def test_jitter():

    o = JitterProducerOperation(IntervalProducer(dt(1, 1), 3600), 60)

    start = dt(1, 0, 59)

    assert o.get_next(start) == dt(1, 1)
    assert o.get_next(start) == dt(1, 1, 0, 30)
    assert o.get_next(start) == dt(1, 1, 1)


def test_jitter_low_ok():

    o = JitterProducerOperation(IntervalProducer(dt(1, 1), 3600), -60, 60)

    start = dt(1, 0, 30)

    assert o.get_next(start) == dt(1, 0, 59)
    assert o.get_next(start) == dt(1, 1, 0)
    assert o.get_next(start) == dt(1, 1, 1)


def test_jitter_shift_forward():

    o = JitterProducerOperation(IntervalProducer(dt(1, 1), 3600), -60, 60)

    start = dt(1, 0, 59, 30)

    assert o.get_next(start) == start
    assert o.get_next(start) == dt(1, 1, 0, 30)
    assert o.get_next(start) == dt(1, 1, 1, 30)
