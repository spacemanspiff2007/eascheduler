from datetime import date as dt_date

import pytest

import eascheduler.producers.prod_filter_holiday as prod_filter_holiday_module
from eascheduler.builder import add_holiday, get_holiday_name, get_holidays_by_name, is_holiday, pop_holiday
from eascheduler.producers.prod_filter_holiday import setup_holidays


@pytest.fixture(autouse=True)
def patch_holidays(monkeypatch):
    monkeypatch.setattr(prod_filter_holiday_module, 'HOLIDAYS', None)
    setup_holidays('DE', 'BE', language='de')


def test_is_holiday():
    assert is_holiday('2024-03-08')
    assert not is_holiday('2024-03-09')


def test_pop_holiday():
    assert pop_holiday('2024-03-08') == 'Internationaler Frauentag'
    assert pop_holiday('2024-03-08') is None


def test_get_holiday_name():
    assert get_holiday_name('2024-03-08') == 'Internationaler Frauentag'
    assert get_holiday_name('2024-03-08') == 'Internationaler Frauentag'


def test_add_and_get_by_name():
    assert get_holidays_by_name('EAScheduler') == []
    add_holiday('2024-01-02', 'EAScheduler Day')
    assert get_holidays_by_name('EAScheduler') == [dt_date(2024, 1, 2)]
    add_holiday('2024-01-03', 'EAScheduler Day')
    assert get_holidays_by_name('EAScheduler') == [dt_date(2024, 1, 2), dt_date(2024, 1, 3)]
    add_holiday('2024-01-03', 'Another Day')
    assert get_holiday_name('2024-01-03') == 'Another Day; EAScheduler Day'
    assert get_holidays_by_name('EAScheduler') == [dt_date(2024, 1, 2), dt_date(2024, 1, 3)]
    assert get_holidays_by_name('Another') == [dt_date(2024, 1, 3)]
