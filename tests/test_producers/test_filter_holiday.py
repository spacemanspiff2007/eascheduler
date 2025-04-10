from datetime import date as dt_date

import pytest
from whenever import SystemDateTime

import eascheduler.producers.prod_filter_holiday as prod_filter_holiday_module
from eascheduler.producers.prod_filter_holiday import (
    HolidayProducerFilter,
    NotWorkDayProducerFilter,
    WorkDayProducerFilter,
    is_holiday,
    pop_holiday,
    setup_holidays,
)
from tests.helper import compare_with_copy


@pytest.fixture(autouse=True)
def patch_holidays(monkeypatch) -> None:
    monkeypatch.setattr(prod_filter_holiday_module, 'HOLIDAYS', None)
    setup_holidays('DE', 'BE', language='de')


def test_holiday_setup() -> None:
    prod_filter_holiday_module.HOLIDAYS = None
    setup_holidays('DE', 'BE', observed=True, language='de')

    prod_filter_holiday_module.HOLIDAYS = None
    setup_holidays('DE', 'BE', observed=False, language='de', categories='catholic')

    prod_filter_holiday_module.HOLIDAYS = None
    setup_holidays('DE', observed=False, language='BE', categories=('catholic', 'public'))


def test_copy() -> None:
    f = HolidayProducerFilter()
    compare_with_copy(f, f.copy())


def test_holiday_filter() -> None:
    f = HolidayProducerFilter()
    assert f.allow(SystemDateTime(2024, 3, 8))      # Internationaler Frauentag
    assert not f.allow(SystemDateTime(2024, 1, 6))  # Heilige Drei Könige nicht


def test_is_holiday() -> None:
    assert is_holiday(dt_date(2024, 3, 8))
    assert not is_holiday(dt_date(2024, 3, 9))


def test_holiday_remove() -> None:
    assert pop_holiday(dt_date(2024, 3, 8)) == 'Internationaler Frauentag'
    assert pop_holiday(dt_date(2024, 3, 9)) is None


def test_working_day_filter() -> None:
    f = WorkDayProducerFilter()
    not_f = NotWorkDayProducerFilter()

    def allow(obj: SystemDateTime) -> bool:
        a = f.allow(obj)
        b = not_f.allow(obj)
        assert a != b
        return a

    assert allow(SystemDateTime(2024, 10, 2))       # Wednesday
    assert allow(SystemDateTime(2024, 10, 2))       # Wednesday
    assert not allow(SystemDateTime(2024, 10, 3))   # Tag der Deutschen Einheit
    assert allow(SystemDateTime(2024, 10, 4))       # Friday
    assert not allow(SystemDateTime(2024, 10, 5))   # Saturday
    assert not allow(SystemDateTime(2024, 10, 6))   # Sunday
    assert allow(SystemDateTime(2024, 10, 7))       # Monday
