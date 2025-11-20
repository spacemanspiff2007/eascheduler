import pytest
from tzlocal import get_localzone_name
from whenever import Time, ZonedDateTime

from eascheduler.helpers import TimeReplacer
from eascheduler.producers import TimeProducer
from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from tests.helper import compare_with_copy, get_ger_str, get_german_as_instant, get_system_as_instant


def test_simple() -> None:
    producer = TimeProducer(TimeReplacer(Time(8), 'after', 'earlier'))

    for _ in range(10):
        assert producer.get_next(get_system_as_instant(1, 1, 7)) == get_system_as_instant(1, 1, 8)
        assert producer.get_next(get_system_as_instant(1, 1, 8)) == get_system_as_instant(1, 2, 8)
        assert producer.get_next(get_system_as_instant(1, 2, 8)) == get_system_as_instant(1, 3, 8)


def test_copy() -> None:
    p = TimeProducer(TimeReplacer(Time(8), 'after', 'earlier'))
    p1 = p.copy()
    compare_with_copy(p, p1)

    p1._filter = DayOfWeekProducerFilter([6])
    compare_with_copy(p, TimeProducer(TimeReplacer(Time(8), 'after', 'earlier')))
    compare_with_copy(p1, p1.copy())


def test_filter() -> None:
    producer = TimeProducer(TimeReplacer(Time(8), 'after', 'earlier'))
    producer._filter = DayOfWeekProducerFilter([6])

    for _ in range(10):
        assert producer.get_next(get_system_as_instant(1, 1, 7)) == get_system_as_instant(1, 6, 8)
        assert producer.get_next(get_system_as_instant(1, 6, 8)) == get_system_as_instant(1, 13, 8)
        assert producer.get_next(get_system_as_instant(1, 13, 8)) == get_system_as_instant(1, 20, 8)


@pytest.mark.parametrize(
    ('time_replacer', 'hour'), [
        pytest.param(TimeReplacer(Time(0, 0), 'after', 'twice'), '00:00:00', id='midnight'),
        pytest.param(
            TimeReplacer(Time(23, 59, 59, nanosecond=999_999_999), 'after', 'twice'),
            '23:59:59.999999999', id='end_of_day'
        ),
    ]
)
def test_time_start_end_of_day(time_replacer: TimeReplacer, hour: str) -> None:

    producer = TimeProducer(time_replacer)

    instant = get_system_as_instant(year=2024, month=1, day=1).subtract(nanoseconds=1)
    assert producer.get_next(instant).to_system_tz().format_iso()[:10] == '2024-01-01'

    days = set()
    s = ZonedDateTime.from_system_tz(2024, 1, 1)
    while s.year == 2024:
        days.add(s.format_iso().split('T')[0])
        s = s.add(hours=24)

    for _ in range(366):    # 2024 is a leap year
        instant = producer.get_next(instant)
        iso = instant.to_system_tz().format_iso()
        day, clock = iso.split('T')
        assert day in days, days
        days.remove(day)
        assert clock.split('+')[0] == hour
    assert not days
    assert instant.to_system_tz().format_iso()[:10] == '2024-12-31'


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_dst_skip() -> None:
    producer = TimeProducer(TimeReplacer(Time(2, 30), 'skip', 'earlier'))

    # one hour jump forward
    start = get_german_as_instant(3, 24, 1)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-03-24T02:30:00+01:00'
        assert get_ger_str(dst_2) == '2001-03-26T02:30:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-27T02:30:00+02:00'


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_dst_close() -> None:
    producer = TimeProducer(TimeReplacer(Time(2, 30), 'after', 'skip'))

    # one hour jump forward
    start = get_german_as_instant(3, 24, 1)

    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)

        assert get_ger_str(dst_1) == '2001-03-24T02:30:00+01:00'
        assert get_ger_str(dst_2) == '2001-03-25T03:00:00+02:00'
        assert get_ger_str(dst_3) == '2001-03-26T02:30:00+02:00'


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_dst_twice() -> None:
    producer = TimeProducer(TimeReplacer(Time(2, 30), 'skip', 'twice'))

    # one hour jump backwards
    start = get_german_as_instant(10, 27, 1, minute=30)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = producer.get_next(start)
        dst_2 = producer.get_next(dst_1)
        dst_3 = producer.get_next(dst_2)
        dst_4 = producer.get_next(dst_3)

        assert get_ger_str(dst_1) == '2001-10-27T02:30:00+02:00'
        assert get_ger_str(dst_2) == '2001-10-28T02:30:00+02:00'
        assert get_ger_str(dst_3) == '2001-10-28T02:30:00+01:00'
        assert get_ger_str(dst_4) == '2001-10-29T02:30:00+01:00'
