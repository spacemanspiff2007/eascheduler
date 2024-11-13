import pytest

from eascheduler.const import get_day_nr, get_month_nr


def test_day_nr() -> None:
    assert get_day_nr('Monday') == 1
    assert get_day_nr('mOn') == 1
    assert get_day_nr('mo') == 1

    with pytest.raises(ValueError, match='Unknown day name: Minday! Did you mean: monday'):
        assert get_day_nr('Minday') == 1
    with pytest.raises(ValueError, match='Unknown day name: asdf'):
        assert get_day_nr('asdf') == 1


def test_month_nr() -> None:
    assert get_month_nr('Januar') == 1
    assert get_month_nr('jAn') == 1

    with pytest.raises(ValueError, match='Unknown month name: Janoar! Did you mean: januar'):
        assert get_month_nr('Janoar') == 1
    with pytest.raises(ValueError, match='Unknown month name: asdf'):
        assert get_month_nr('asdf') == 1
