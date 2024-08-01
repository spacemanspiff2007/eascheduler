import pytest
from whenever import Time

import eascheduler.producers.prod_operation as prod_operation_module
from eascheduler.helpers import TimeReplacer
from eascheduler.producers.prod_interval import IntervalProducer
from eascheduler.producers.prod_operation import (
    EarliestProducerOperation,
    JitterProducerOperation,
    LatestProducerOperation,
    OffsetProducerOperation,
)
from tests.helper import get_system_as_instant


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


def test_offset():

    o = OffsetProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 0), 3600), -3600 * 10)

    for _ in range(10):
        assert o.get_next(get_system_as_instant(1, 1, 3)) == get_system_as_instant(1, 1, 4)
        assert o.get_next(get_system_as_instant(1, 1, 4)) == get_system_as_instant(1, 1, 5)
        assert o.get_next(get_system_as_instant(1, 1, 5)) == get_system_as_instant(1, 1, 6)

    o = OffsetProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 0), 3600), 300)

    for _ in range(10):
        assert o.get_next(get_system_as_instant(1, 1, 3)) == get_system_as_instant(1, 1, 4, 5)
        assert o.get_next(get_system_as_instant(1, 1, 4)) == get_system_as_instant(1, 1, 5, 5)
        assert o.get_next(get_system_as_instant(1, 1, 5)) == get_system_as_instant(1, 1, 6, 5)

    o = OffsetProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 0), 3600), -300)

    for _ in range(10):
        assert o.get_next(get_system_as_instant(1, 1, 3)) == get_system_as_instant(1, 1, 3, 55)
        assert o.get_next(get_system_as_instant(1, 1, 4)) == get_system_as_instant(1, 1, 4, 55)
        assert o.get_next(get_system_as_instant(1, 1, 5)) == get_system_as_instant(1, 1, 5, 55)


def test_earliest():

    o = EarliestProducerOperation(IntervalProducer(
        get_system_as_instant(1, 1, 0), 3600),
        TimeReplacer(Time(8, 0, 0), 'close', 'twice')
    )

    for _ in range(10):
        assert o.get_next(get_system_as_instant(1, 1, 3)) == get_system_as_instant(1, 1, 8)
        assert o.get_next(get_system_as_instant(1, 1, 7, 1)) == get_system_as_instant(1, 1, 8)
        assert o.get_next(get_system_as_instant(1, 1, 22)) == get_system_as_instant(1, 1, 23)
        assert o.get_next(get_system_as_instant(1, 1, 23)) == get_system_as_instant(1, 2, 8)


def test_latest():

    o = LatestProducerOperation(
        IntervalProducer(get_system_as_instant(1, 1, 0, 30), 3600),
        TimeReplacer(Time(8, 0, 0), 'close', 'twice')
    )

    for _ in range(10):
        assert o.get_next(get_system_as_instant(1, 1, 7)) == get_system_as_instant(1, 1, 7, 30)
        assert o.get_next(get_system_as_instant(1, 1, 7, 59)) == get_system_as_instant(1, 1, 8)
        assert o.get_next(get_system_as_instant(1, 1, 8)) == get_system_as_instant(1, 2, 0, 30)


def test_jitter():

    o = JitterProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 1), 3600), 60)

    start = get_system_as_instant(1, 1, 0, 59)

    for _ in range(10):
        assert o.get_next(start) == get_system_as_instant(1, 1, 1)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 0, 30)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 1)


def test_jitter_low_ok():

    o = JitterProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 1), 3600), -60, 60)

    start = get_system_as_instant(1, 1, 0, 30)

    for _ in range(10):
        assert o.get_next(start) == get_system_as_instant(1, 1, 0, 59)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 0)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 1)


def test_jitter_shift_forward():

    o = JitterProducerOperation(IntervalProducer(get_system_as_instant(1, 1, 1), 3600), -60, 60)

    start = get_system_as_instant(1, 1, 0, 59, 30)

    for _ in range(10):
        assert o.get_next(start) == get_system_as_instant(1, 1, 0, 59, 30, microsecond=100)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 0, 30, microsecond=100)
        assert o.get_next(start) == get_system_as_instant(1, 1, 1, 1, 30, microsecond=100)
