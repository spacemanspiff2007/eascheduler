from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from eascheduler.producers.prod_interval import IntervalProducer
from tests.helper import compare_with_copy, get_ger_str, get_german_as_instant, get_system_as_instant


def test_first() -> None:
    p = IntervalProducer(get_system_as_instant(1, 1, 8), 5)
    assert p.get_next(get_system_as_instant(1, 1, 8, second=3)) == get_system_as_instant(1, 1, 8, second=5)

    p = IntervalProducer(get_system_as_instant(1, 1, 8), 5)
    assert p.get_next(get_system_as_instant(1, 1, 8, second=5)) == get_system_as_instant(1, 1, 8, second=10)

    p = IntervalProducer(None, 5)
    assert p.get_next(get_system_as_instant(1, 1, 8)) == get_system_as_instant(1, 1, 8, microsecond=1)


def test_simple() -> None:
    dt_now = get_system_as_instant(1, 1, 0)
    p = IntervalProducer(get_system_as_instant(1, 1, 8), 3600 * 5)

    for v in range(3, 100, 5):
        days = v // 24
        hours = v % 24
        for _ in range(20):
            assert p.get_next(dt_now) == get_system_as_instant(1, 1 + days, hours)
        dt_now = get_system_as_instant(1, 1 + days, hours)


def test_filter() -> None:
    producer = IntervalProducer(get_system_as_instant(1, 1, 8), 3600 * 12)

    for _ in range(10):
        assert producer.get_next(get_system_as_instant(1, 1, 7)) == get_system_as_instant(1, 1, 8)
        assert producer.get_next(get_system_as_instant(1, 1, 8)) == get_system_as_instant(1, 1, 20)
        assert producer.get_next(get_system_as_instant(1, 1, 20)) == get_system_as_instant(1, 2, 8)

    producer._filter = DayOfWeekProducerFilter([6])
    for _ in range(10):
        assert producer.get_next(get_system_as_instant(1, 1, 7)) == get_system_as_instant(1, 6, 8)
        assert producer.get_next(get_system_as_instant(1, 6, 8)) == get_system_as_instant(1, 6, 20)
        assert producer.get_next(get_system_as_instant(1, 6, 20)) == get_system_as_instant(1, 13, 8)


def test_dst() -> None:
    # one hour jump forward
    start = get_german_as_instant(3, 25, 0, 30)
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
    start = get_german_as_instant(10, 28, 1, 30)
    producer = IntervalProducer(start, 3600)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_3) == '2001-10-28T03:30:00+01:00'


def test_cmp() -> None:
    start = get_german_as_instant(3, 25, 0, 30)
    producer = IntervalProducer(start, 3600)
    assert producer == IntervalProducer(start, 3600)


def test_copy() -> None:
    p = IntervalProducer(None, 3600)
    compare_with_copy(p, p.copy())

    p._filter = DayOfWeekProducerFilter([6])
    compare_with_copy(p, p.copy())
