from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from eascheduler.producers.prod_interval import IntervalProducer
from tests.helper import cmp_utc_with_german, get_ger_str, get_local_as_utc


def test_simple():
    dt_start = get_local_as_utc(1, 1, 1)
    dt_now = dt_start

    p = IntervalProducer(get_local_as_utc(1, 1, 8), 3600 * 5)

    for v in range(3, 100, 5):
        days = v // 24
        hours = v % 24
        for _ in range(20):
            cmp_utc_with_german(p.get_next(dt_now), 1, dt_start.day + days, hours)
        dt_now = get_local_as_utc(1, dt_start.day + days, hours)


def test_filter():
    producer = IntervalProducer(get_local_as_utc(1, 1, 8), 3600 * 12)

    for _ in range(10):
        assert producer.get_next(get_local_as_utc(1, 1, 7)) == get_local_as_utc(1, 1, 8)
        assert producer.get_next(get_local_as_utc(1, 1, 8)) == get_local_as_utc(1, 1, 20)
        assert producer.get_next(get_local_as_utc(1, 1, 20)) == get_local_as_utc(1, 2, 8)

    producer._filter = DayOfWeekProducerFilter([6])
    for _ in range(10):
        assert producer.get_next(get_local_as_utc(1, 1, 7)) == get_local_as_utc(1, 6, 8)
        assert producer.get_next(get_local_as_utc(1, 6, 8)) == get_local_as_utc(1, 6, 20)
        assert producer.get_next(get_local_as_utc(1, 6, 20)) == get_local_as_utc(1, 13, 8)


def test_dst():
    # one hour jump forward
    start = get_local_as_utc(3, 25, 0, 30)
    producer = IntervalProducer(start, 3600)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(start) == '2001-03-25T00:30:00+01:00'
        assert get_ger_str(dst_1) == '2001-03-25T01:30:00+01:00'
        assert get_ger_str(dst_2) == '2001-03-25T03:30:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-25T04:30:00+02:00'

    # one hour jump backwards
    start = get_local_as_utc(10, 28, 1, 30)
    producer = IntervalProducer(start, 3600)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_3) == '2001-10-28T03:30:00+01:00'
