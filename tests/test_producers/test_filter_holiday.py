from datetime import date as dt_date

import pytest
from whenever import SYSTEM_TZ, ZonedDateTime

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
    assert f.allow(ZonedDateTime(2024, 3, 8, tz=SYSTEM_TZ))      # Internationaler Frauentag
    assert not f.allow(ZonedDateTime(2024, 1, 6, tz=SYSTEM_TZ))  # Heilige Drei Könige nicht


def test_is_holiday() -> None:
    assert is_holiday(dt_date(2024, 3, 8))
    assert not is_holiday(dt_date(2024, 3, 9))


def test_holiday_remove() -> None:
    assert pop_holiday(dt_date(2024, 3, 8)) == 'Frauentag'
    assert pop_holiday(dt_date(2024, 3, 9)) is None


def test_working_day_filter() -> None:
    f = WorkDayProducerFilter()
    not_f = NotWorkDayProducerFilter()

    def allow(obj: ZonedDateTime) -> bool:
        a = f.allow(obj)
        b = not_f.allow(obj)
        assert a != b
        return a

    assert allow(ZonedDateTime(2024, 10, 2, tz=SYSTEM_TZ))       # Wednesday
    assert allow(ZonedDateTime(2024, 10, 2, tz=SYSTEM_TZ))       # Wednesday
    assert not allow(ZonedDateTime(2024, 10, 3, tz=SYSTEM_TZ))   # Tag der Deutschen Einheit
    assert allow(ZonedDateTime(2024, 10, 4, tz=SYSTEM_TZ))       # Friday
    assert not allow(ZonedDateTime(2024, 10, 5, tz=SYSTEM_TZ))   # Saturday
    assert not allow(ZonedDateTime(2024, 10, 6, tz=SYSTEM_TZ))   # Sunday
    assert allow(ZonedDateTime(2024, 10, 7, tz=SYSTEM_TZ))       # Monday
