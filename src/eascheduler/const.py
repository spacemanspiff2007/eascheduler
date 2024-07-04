from collections.abc import Iterable
from datetime import date as dt_date
from typing import Final


DAY_NAMES: Final[dict[str, int]] = {}
MONTH_NAMES: Final[dict[str, int]] = {}


def __create_names() -> None:
    values: dict[str, int] = {}

    def _set_in_values(key: str, value: int):
        if key in values and values[key] != value:
            msg = f'Duplicate value for key {key}: {values[key]} and {value}'
            raise ValueError(msg)
        values[key] = value

    def add_values(objs: Iterable[str], cut: int | None) -> None:
        for nr, day in enumerate(objs, start=1):
            _set_in_values(day.lower(), nr)
            if cut:
                _set_in_values(day[:cut].lower(), nr)

    def to_dict(dst: dict) -> None:
        for key, value in sorted(values.items(), key=lambda x: (x[1], x[0])):
            dst[key] = value
        values.clear()

    # Days in local timezone
    for i in range(1, 8):
        _set_in_values(dt_date(2001, 1, i).strftime('%A').lower(), i)
        _set_in_values(dt_date(2001, 1, i).strftime('%a').lower(), i)

    # Days in German and English
    add_values(['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], 2)
    add_values(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 3)

    to_dict(DAY_NAMES)

    # Months in local timezone
    for i in range(1, 13):
        _set_in_values(dt_date(2001, i, 1).strftime('%B').lower(), i)
        _set_in_values(dt_date(2001, i, 1).strftime('%b').lower(), i)

    # Month in German
    add_values(['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober',
                'November', 'Dezember'], 3)
    values['mrz'] = 3

    # Month in English
    add_values(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                'November', 'December'], 3)

    to_dict(MONTH_NAMES)


__create_names()
del __create_names
