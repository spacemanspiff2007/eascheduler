from datetime import time as dt_time

import pytest
from tzlocal import get_localzone_name
from whenever import Time

from eascheduler.producers import TimeProducer
from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from tests.helper import get_ger_str, get_german_as_instant, get_local_as_instant


def test_simple():
    producer = TimeProducer(Time(8))

    for _ in range(10):
        assert producer.get_next(get_local_as_instant(1, 1, 7)) == get_local_as_instant(1, 1, 8)
        assert producer.get_next(get_local_as_instant(1, 1, 8)) == get_local_as_instant(1, 2, 8)
        assert producer.get_next(get_local_as_instant(1, 2, 8)) == get_local_as_instant(1, 3, 8)


def test_filter():
    producer = TimeProducer(Time(8))
    producer._filter = DayOfWeekProducerFilter([6])

    for _ in range(10):
        assert producer.get_next(get_local_as_instant(1, 1, 7)) == get_local_as_instant(1, 6, 8)
        assert producer.get_next(get_local_as_instant(1, 6, 8)) == get_local_as_instant(1, 13, 8)
        assert producer.get_next(get_local_as_instant(1, 13, 8)) == get_local_as_instant(1, 20, 8)


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_dst():
    producer = TimeProducer(Time(2, 30))

    # one hour jump forward
    start = get_german_as_instant(3, 24, 1)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-03-24T02:30:00+01:00'
        assert get_ger_str(dst_2) == '2001-03-26T02:30:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-27T02:30:00+02:00'

    # one hour jump backwards
    start = get_german_as_instant(10, 28, 1, minute=30)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_3) == '2001-10-29T02:30:00+01:00'
