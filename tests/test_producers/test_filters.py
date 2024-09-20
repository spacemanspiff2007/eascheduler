from datetime import date as dt_date
from datetime import datetime as dt_datetime

import pytest
from whenever import SystemDateTime, Time, patch_current_time

import eascheduler.producers.prod_filter as prod_filter_module
from eascheduler.builder import is_holiday
from eascheduler.producers.prod_filter import (
    AllGroupProducerFilter,
    AnyGroupProducerFilter,
    DayOfMonthProducerFilter,
    DayOfWeekProducerFilter,
    HolidayProducerFilter,
    InvertingProducerFilter,
    MonthOfYearProducerFilter,
    TimeProducerFilter,
    setup_holidays,
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


@pytest.fixture(autouse=True)
def patch_holidays(monkeypatch):
    monkeypatch.setattr(prod_filter_module, 'HOLIDAYS', None)
    setup_holidays('DE', 'BE')


def test_holiday_setup():
    prod_filter_module.HOLIDAYS = None
    setup_holidays('DE', 'BE', observed=True, language='de')

    prod_filter_module.HOLIDAYS = None
    setup_holidays('DE', 'BE', observed=False, language='de', categories='catholic')

    prod_filter_module.HOLIDAYS = None
    setup_holidays('DE', observed=False, language='BE', categories=('catholic', 'public'))


def test_holiday_filter():
    f = HolidayProducerFilter()
    assert f.allow(SystemDateTime(2024, 3, 8))      # Internationaler Frauentag
    assert not f.allow(SystemDateTime(2024, 1, 6))  # Heilige Drei Könige nicht


def test_holiday_func():
    assert is_holiday(dt_date(2024, 3, 8))
    assert is_holiday(dt_datetime(2024, 3, 8, 12, 30))
    assert is_holiday('2024-03-08')

    s = SystemDateTime(2024, 3, 8, 12)
    with patch_current_time(s, keep_ticking=False):
        assert is_holiday(None)

    assert is_holiday(s.date())
    assert is_holiday(s)
    assert is_holiday(s.instant())

    assert not is_holiday(dt_date(2024, 3, 9))
