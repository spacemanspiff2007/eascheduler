from datetime import time as dt_time

import pytest
from tzlocal import get_localzone_name
from whenever import Time

import eascheduler.producers.prod_operation as prod_operation_module
from eascheduler.producers.prod_interval import IntervalProducer
from eascheduler.producers.prod_operation import (
    EarliestProducerOperation,
    JitterProducerOperation,
    LatestProducerOperation,
    OffsetProducerOperation,
)
from tests.helper import get_ger_str, get_german_as_instant, get_local_as_instant


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

    o = OffsetProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 0), 3600), -3600 * 10)

    for _ in range(10):
        assert o.get_next(get_local_as_instant(1, 1, 3)) == get_local_as_instant(1, 1, 4)
        assert o.get_next(get_local_as_instant(1, 1, 4)) == get_local_as_instant(1, 1, 5)
        assert o.get_next(get_local_as_instant(1, 1, 5)) == get_local_as_instant(1, 1, 6)

    o = OffsetProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 0), 3600), 300)

    for _ in range(10):
        assert o.get_next(get_local_as_instant(1, 1, 3)) == get_local_as_instant(1, 1, 4, 5)
        assert o.get_next(get_local_as_instant(1, 1, 4)) == get_local_as_instant(1, 1, 5, 5)
        assert o.get_next(get_local_as_instant(1, 1, 5)) == get_local_as_instant(1, 1, 6, 5)

    o = OffsetProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 0), 3600), -300)

    for _ in range(10):
        assert o.get_next(get_local_as_instant(1, 1, 3)) == get_local_as_instant(1, 1, 3, 55)
        assert o.get_next(get_local_as_instant(1, 1, 4)) == get_local_as_instant(1, 1, 4, 55)
        assert o.get_next(get_local_as_instant(1, 1, 5)) == get_local_as_instant(1, 1, 5, 55)


def test_earliest():

    o = EarliestProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 0), 3600), Time(8, 0, 0))

    for _ in range(10):
        assert o.get_next(get_local_as_instant(1, 1, 3)) == get_local_as_instant(1, 1, 8)
        assert o.get_next(get_local_as_instant(1, 1, 7, 1)) == get_local_as_instant(1, 1, 8)
        assert o.get_next(get_local_as_instant(1, 1, 22)) == get_local_as_instant(1, 1, 23)
        assert o.get_next(get_local_as_instant(1, 1, 23)) == get_local_as_instant(1, 2, 8)


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_earliest_dst():
    o = EarliestProducerOperation(
        IntervalProducer(get_local_as_instant(3, 24, 1), 3600),
        Time(2, 30, 0)
    )

    # one hour jump forward
    start = get_german_as_instant(3, 25, hour=0)

    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)

        assert get_ger_str(start) == '2001-03-25T00:00:00+01:00'
        assert get_ger_str(dst_1) == '2001-03-25T03:00:00+02:00'
        assert get_ger_str(dst_2) == '2001-03-25T04:00:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-25T05:00:00+02:00'

    # one hour jump backwards
    start = get_german_as_instant(10, 28, 1, minute=30)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_3) == '2001-10-28T03:00:00+01:00'


def test_latest():

    o = LatestProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 0, 30), 3600), Time(8, 0, 0))

    for _ in range(10):
        assert o.get_next(get_local_as_instant(1, 1, 7)) == get_local_as_instant(1, 1, 7, 30)
        assert o.get_next(get_local_as_instant(1, 1, 7, 59)) == get_local_as_instant(1, 1, 8)
        assert o.get_next(get_local_as_instant(1, 1, 8)) == get_local_as_instant(1, 2, 0, 30)


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_latest_dst():
    o = LatestProducerOperation(
        IntervalProducer(get_local_as_instant(3, 24, hour=0), 3600),
        Time(2, 30, 0)
    )

    # one hour jump forward
    start = get_german_as_instant(3, 25, hour=0)

    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)
        dst_4 = o.get_next(dst_3)

        assert get_ger_str(start) == '2001-03-25T00:00:00+01:00'
        assert get_ger_str(dst_1) == '2001-03-25T01:00:00+01:00'
        assert get_ger_str(dst_2) == '2001-03-25T03:00:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-26T00:00:00+02:00'
        assert get_ger_str(dst_4) == '2001-03-26T01:00:00+02:00'

    # one hour jump backwards
    start = get_german_as_instant(10, 28, 1, minute=30)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)
        dst_4 = o.get_next(dst_3)
        dst_5 = o.get_next(dst_4)

        assert get_ger_str(dst_1) == '2001-10-28T02:00:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_3) == '2001-10-28T02:00:00+01:00'
        assert get_ger_str(dst_4) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_5) == '2001-10-29T00:00:00+01:00'




def test_jitter():

    o = JitterProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 1), 3600), 60)

    start = get_local_as_instant(1, 1, 0, 59)

    for _ in range(10):
        assert o.get_next(start) == get_local_as_instant(1, 1, 1)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 0, 30)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 1)


def test_jitter_low_ok():

    o = JitterProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 1), 3600), -60, 60)

    start = get_local_as_instant(1, 1, 0, 30)

    for _ in range(10):
        assert o.get_next(start) == get_local_as_instant(1, 1, 0, 59)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 0)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 1)


def test_jitter_shift_forward():

    o = JitterProducerOperation(IntervalProducer(get_local_as_instant(1, 1, 1), 3600), -60, 60)

    start = get_local_as_instant(1, 1, 0, 59, 30)

    for _ in range(10):
        assert o.get_next(start) == get_local_as_instant(1, 1, 0, 59, 30, microsecond=100)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 0, 30, microsecond=100)
        assert o.get_next(start) == get_local_as_instant(1, 1, 1, 1, 30, microsecond=100)
