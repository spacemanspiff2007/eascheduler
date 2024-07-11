from datetime import time as dt_time

from whenever import SystemDateTime, Time

from eascheduler.producers.prod_filter import (
    AllGroupProducerFilter,
    AnyGroupProducerFilter,
    DayOfMonthProducerFilter,
    DayOfWeekProducerFilter,
    InvertingProducerFilter,
    MonthOfYearProducerFilter,
    TimeProducerFilter,
)


def test_time_filter():
    f = TimeProducerFilter(lower=Time(8))
    assert not f.allow(SystemDateTime(2001, 1, 1, 7, 59))
    assert f.allow(SystemDateTime(2001, 1, 1, 8))

    f = TimeProducerFilter(upper=Time(8))
    assert f.allow(SystemDateTime(2001, 1, 1, 7, 59))
    assert not f.allow(SystemDateTime(2001, 1, 1, 8))
    assert not f.allow(SystemDateTime(2001, 1, 1, 8, 0, 1))

    f = TimeProducerFilter(lower=Time(7), upper=Time(8))
    assert not f.allow(SystemDateTime(2001, 1, 1, 6, 59))
    assert f.allow(SystemDateTime(2001, 1, 1, 7))
    assert f.allow(SystemDateTime(2001, 1, 1, 7, 59, 59))
    assert not f.allow(SystemDateTime(2001, 1, 1, 8, 0))


def test_dow_filter():
    f = DayOfWeekProducerFilter([2, 3, 4, 5, 6, 7])
    assert not f.allow(SystemDateTime(2001, 1, 1))

    for i in range(2, 7):
        assert f.allow(SystemDateTime(2001, 1, i))

    assert not f.allow(SystemDateTime(2001, 1, 8))


def test_dom_filter():
    f = DayOfMonthProducerFilter(list(range(2, 31)))
    assert not f.allow(SystemDateTime(2001, 1, 1))

    for i in range(2, 31):
        assert f.allow(SystemDateTime(2001, 1, i))

    assert not f.allow(SystemDateTime(2001, 2, 1))


def test_moy_filter():
    f = MonthOfYearProducerFilter([1, 3, 4])
    assert f.allow(SystemDateTime(2001, 1, 31))

    for i in range(1, 29):
        assert not f.allow(SystemDateTime(2001, 2, i))

    assert f.allow(SystemDateTime(2001, 3, 1))


def test_inverting_filter():
    f = InvertingProducerFilter(DayOfWeekProducerFilter([2, 3, 4, 5, 6, 7]))
    assert f.allow(SystemDateTime(2001, 1, 1))

    for i in range(2, 7):
        assert not f.allow(SystemDateTime(2001, 1, i))

    assert f.allow(SystemDateTime(2001, 1, 8))


def test_or_group():
    f = AnyGroupProducerFilter([DayOfWeekProducerFilter([3, 4, 5, 6, 7]), DayOfWeekProducerFilter([1, 4, 5, 6, 7])])
    assert f.allow(SystemDateTime(2001, 1, 1))
    assert not f.allow(SystemDateTime(2001, 1, 2))
    assert f.allow(SystemDateTime(2001, 1, 3))
    assert f.allow(SystemDateTime(2001, 1, 4))


def test_and_group():
    f = AllGroupProducerFilter([DayOfWeekProducerFilter([3, 4, 5, 6, 7]), DayOfWeekProducerFilter([1, 4, 5, 6, 7])])
    assert not f.allow(SystemDateTime(2001, 1, 1))
    assert not f.allow(SystemDateTime(2001, 1, 2))
    assert not f.allow(SystemDateTime(2001, 1, 3))
    assert f.allow(SystemDateTime(2001, 1, 4))
